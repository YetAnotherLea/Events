from flask import Flask, jsonify, request, g
from flask_cors import CORS
import requests
import firebase_admin
from firebase_admin import credentials, auth
import os
from datetime import date
from urllib.parse import unquote

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialisation Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json"))
    firebase_admin.initialize_app(cred)

BASE_URL = 'https://public.opendatasoft.com/api/records/1.0/search/'
DATASET = 'evenements-publics-openagenda'

# Fonction pour récupérer l'utilisateur courant via Firebase
def get_current_user_uid(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        decoded = auth.verify_id_token(token)
        return decoded['uid']
    except:
        return None

# Endpoint événements : filtrage ville et année, à venir par défaut, ordre chronologique
@app.route('/api/events')
def get_events():
    city_filter = request.args.get('city', '').strip()
    year_filter = request.args.get('year', '').strip()
    rows = int(request.args.get('rows', 100))
    page = int(request.args.get('page', 1))

    # Syntaxe de requête OpenDataSoft v1 ; sort=-champ trie en ordre croissant
    if year_filter.isdigit() and len(year_filter) == 4:
        clauses = [f'firstdate_begin>={year_filter}-01-01 AND firstdate_begin<={year_filter}-12-31']
    else:
        clauses = [f'firstdate_begin>={date.today().isoformat()}']
    if city_filter:
        clauses.append('location_city:"%s"' % city_filter.replace('"', ''))

    params = {
        'dataset': DATASET,
        'rows': rows,
        'start': (page - 1) * rows,
        'sort': '-firstdate_begin',
        'q': ' AND '.join(clauses),
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({'error': f'Impossible de récupérer les événements: {str(e)}'}), 500

    data = response.json()
    events = [record.get('fields', {}) for record in data.get('records', [])]
    return jsonify(events)

# Endpoint pour synchroniser utilisateur Firebase dans la base locale
@app.route("/api/users/sync", methods=["POST"])
def sync_user():
    data = request.get_json()
    id_token = data.get("idToken")
    proposed_pseudo = data.get("pseudo", "")
    
    decoded = auth.verify_id_token(id_token)
    uid = decoded["uid"]
    email = decoded.get("email", "")
    name = decoded.get("name", "")
    photo = None

    from Database import get_db
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE firebase_uid = %s", (uid,))
    user = cursor.fetchone()

    if not user:
        pseudo_to_use = proposed_pseudo or name or (email.split('@')[0] if email else "user")

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE pseudo = %s", (pseudo_to_use,))
        result = cursor.fetchone()
        
        if result['count'] > 0:
            if proposed_pseudo:
                cursor.close()
                return jsonify({"error": "Ce pseudo est déjà utilisé", "code": "PSEUDO_TAKEN"}), 400
            else:
                base_pseudo = pseudo_to_use
                counter = 1
                while result['count'] > 0:
                    pseudo_to_use = f"{base_pseudo}{counter}"
                    cursor.execute("SELECT COUNT(*) as count FROM users WHERE pseudo = %s", (pseudo_to_use,))
                    result = cursor.fetchone()
                    counter += 1

        cursor.execute(
            "INSERT INTO users (firebase_uid, pseudo, email, avatar_url) VALUES (%s, %s, %s, %s)",
            (uid, pseudo_to_use, email, None)
        )
        db.commit()
        
        cursor.execute("SELECT * FROM users WHERE firebase_uid = %s", (uid,))
        user = cursor.fetchone()

    cursor.close()
    return jsonify({
        "status": "ok",
        "user": {
            "pseudo": user['pseudo'],
            "email": user['email'],
            "avatar_url": user['avatar_url']
        }
    })

# Récupérer l'utilisateur courant
@app.route("/api/users/me", methods=["GET"])
def get_current_user():
    current_user_uid = get_current_user_uid(request)
    if not current_user_uid:
        return jsonify({"error": "Authentification requise"}), 401
    
    from Database import get_db
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT pseudo, email, avatar_url FROM users WHERE firebase_uid = %s", (current_user_uid,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    cursor.close()
    return jsonify(user)

# Profil utilisateur par pseudo
@app.route("/api/users/<pseudo>", methods=["GET"])
def get_user_profile(pseudo):
    pseudo = unquote(pseudo)
    
    current_user_uid = get_current_user_uid(request)
    if not current_user_uid:
        return jsonify({"error": "Authentification requise"}), 401

    from Database import get_db
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE pseudo = %s", (pseudo,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    cursor.execute("SELECT * FROM users WHERE firebase_uid = %s", (current_user_uid,))
    current_user = cursor.fetchone()
    
    is_own_profile = current_user and current_user['id'] == user['id']

    profile_data = {
        "pseudo": user['pseudo'],
        "avatar_url": user['avatar_url'],
        "bio": user.get('bio', ''),
        "created_at": user['created_at'].isoformat() if user['created_at'] else None,
        "is_own_profile": is_own_profile
    }

    if is_own_profile:
        profile_data["email"] = user['email']

    cursor.close()
    return jsonify(profile_data)

# Modifier profil utilisateur
@app.route("/api/users/<pseudo>", methods=["PUT"])
def update_user_profile(pseudo):
    pseudo = unquote(pseudo)
    
    current_user_uid = get_current_user_uid(request)
    if not current_user_uid:
        return jsonify({"error": "Authentification requise"}), 401

    from Database import get_db
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM users 
        WHERE pseudo = %s AND firebase_uid = %s
    """, (pseudo, current_user_uid))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return jsonify({"error": "Vous ne pouvez modifier que votre propre profil"}), 403

    data = request.get_json()
    bio = data.get('bio', user.get('bio', ''))
    avatar_url = data.get('avatar_url', user.get('avatar_url', ''))

    cursor.execute("""
        UPDATE users 
        SET bio = %s, avatar_url = %s 
        WHERE id = %s
    """, (bio, avatar_url, user['id']))
    
    db.commit()
    cursor.close()
    return jsonify({"status": "ok", "message": "Profil mis à jour"})

# Fermeture de connexion à la DB
@app.teardown_appcontext
def close_db_connection(error):
    from Database import close_db
    close_db(error)

# Récupérer un événement par UID
@app.route('/api/events/<uid>')
def get_event(uid):
    try:
        response = requests.get(BASE_URL, params={'dataset': DATASET, 'refine.uid': uid}, timeout=10)
        response.raise_for_status()
        records = response.json().get('records', [])
        if not records:
            return jsonify({'error': 'Événement introuvable'}), 404
        return jsonify(records[0]['fields'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
