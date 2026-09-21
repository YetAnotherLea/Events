from flask import Flask, jsonify, request, g
from flask_cors import CORS
import requests
import firebase_admin
from firebase_admin import credentials, auth
import os
import re
from datetime import date
from urllib.parse import unquote

app = Flask(__name__)
# En prod le front est servi sur la même origine : CORS ne sert qu'en développement
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")}})

# Initialisation Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json"))
    firebase_admin.initialize_app(cred)

BASE_URL = 'https://public.opendatasoft.com/api/records/1.0/search/'
DATASET = 'evenements-publics-openagenda'

MAX_ROWS = 100
PSEUDO_RE = re.compile(r'^[\w.-]{1,50}$')
PSEUDOS_RESERVES = {'me', 'sync'}
MAX_BIO = 1000
# Avatar en data URL base64 ; ~1 Mo décodé, borne aussi par client_max_body_size côté nginx
MAX_AVATAR = 1_400_000
AVATAR_RE = re.compile(r'^data:image/(png|jpeg|webp|gif);base64,[A-Za-z0-9+/=]+$')

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
    try:
        rows = min(max(int(request.args.get('rows', MAX_ROWS)), 1), MAX_ROWS)
        page = max(int(request.args.get('page', 1)), 1)
    except ValueError:
        return jsonify({'error': 'Paramètres rows et page invalides'}), 400

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
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken")
    proposed_pseudo = str(data.get("pseudo") or "").strip()

    if not id_token:
        return jsonify({"error": "idToken manquant"}), 400
    if proposed_pseudo and (not PSEUDO_RE.match(proposed_pseudo) or proposed_pseudo.lower() in PSEUDOS_RESERVES):
        return jsonify({"error": "Pseudo invalide", "code": "PSEUDO_INVALID"}), 400
    try:
        decoded = auth.verify_id_token(id_token)
    except Exception:
        return jsonify({"error": "Jeton invalide"}), 401
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
        # Pseudo déduit du profil Google/Facebook : borné pour laisser la place au suffixe numérique
        pseudo_to_use = proposed_pseudo or (name or (email.split('@')[0] if email else "user"))[:45]

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

    data = request.get_json(silent=True) or {}
    bio = data.get('bio', user.get('bio', ''))
    avatar_url = data.get('avatar_url', user.get('avatar_url', ''))

    if not isinstance(bio, str) or len(bio) > MAX_BIO:
        cursor.close()
        return jsonify({"error": f"Bio trop longue ({MAX_BIO} caractères max)"}), 400
    if not isinstance(avatar_url, str) or len(avatar_url) > MAX_AVATAR:
        cursor.close()
        return jsonify({"error": "Avatar trop volumineux (1 Mo max)"}), 400
    if avatar_url and avatar_url != 'default_avatar.png' and not AVATAR_RE.match(avatar_url):
        cursor.close()
        return jsonify({"error": "Format d'avatar invalide"}), 400

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
    except Exception:
        app.logger.exception("Récupération de l'événement %s", uid)
        return jsonify({'error': "Impossible de récupérer l'événement"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
