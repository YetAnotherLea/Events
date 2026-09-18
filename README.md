# Events

<p align="center">
  <img src="./frontend/src/assets/logos/eventalis.png" alt="Eventalis" width="120"/>
</p>

<p align="center">
  <img loading="lazy" src="https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs&logoColor=white"/>
  <img loading="lazy" src="https://img.shields.io/badge/Vite-7.1-646CFF?logo=vite&logoColor=white"/>
  <img loading="lazy" src="https://img.shields.io/badge/Flask-Python_3.12-000000?logo=flask&logoColor=white"/>
  <img loading="lazy" src="https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql&logoColor=white"/>
  <img loading="lazy" src="https://img.shields.io/badge/Firebase-Auth-FFCA28?logo=firebase&logoColor=black"/>
  <img loading="lazy" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white"/>
  <img loading="lazy" src="https://img.shields.io/badge/PWA-installable-5A0FC8?logo=pwa&logoColor=white"/>
</p>

🌐 **Démo en ligne : [events.leaballester.com](https://events.leaballester.com)**

**Objectif** : proposer une application web permettant de rechercher des événements publics en France et, à terme, d'organiser des sorties entre utilisateurs autour de ces événements.

Les données proviennent du jeu de données ouvert [`evenements-publics-openagenda`](https://public.opendatasoft.com/explore/dataset/evenements-publics-openagenda/) d'OpenDataSoft, interrogé par une API Flask qui gère également les comptes utilisateurs (authentification Firebase + profils stockés en MySQL).

L'application est une **PWA installable** : elle est pensée pour être consultée aussi bien depuis un navigateur desktop que depuis un mobile connecté au même réseau.

## Sommaire

1. [Prérequis](#-prérequis)
2. [Installation](#-installation)
3. [Démarrage](#-démarrage)
4. [Architecture](#-architecture)
5. [Fonctionnalités](#-fonctionnalités)
6. [API](#-api)
7. [Base de données](#-base-de-données)
8. [Stack technique](#-stack-technique)
9. [Pistes d'amélioration](#-pistes-damélioration)
10. [Auteurs](#-auteurs)

---

## 🧰 Prérequis

- [Docker](https://www.docker.com/) et Docker Compose
- Un serveur **MySQL** accessible depuis les conteneurs (installation locale, XAMPP/MAMP, ou conteneur dédié)
- Un projet **Firebase** avec l'authentification activée (Email/Mot de passe, Google, Facebook)
- PHP en CLI (facultatif, uniquement pour le script `start.php`)

---

## 🔧 Installation

### 1. Cloner le dépôt

```bash
git clone git@github.com:YetAnotherLea/Events.git
cd Events
```

### 2. Créer le fichier `.env` à la racine

```dotenv
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
DB_NAME=nom_de_votre_db
DB_HOST=host.docker.internal
VITE_API_URL=http://localhost:5000
```

> `DB_HOST=host.docker.internal` permet au conteneur backend de joindre le MySQL de la machine hôte.
>
> En production, le front et l'API sont servis sur la même origine : laisser `VITE_API_URL` vide
> pour que les appels soient relatifs (`/api/...`).
>
> Pour tester la PWA depuis un téléphone, remplacez `localhost` par l'adresse IP de votre machine sur le réseau Wi-Fi :
> `VITE_API_URL=http://192.168.x.x:5000`

### 3. Créer la base de données

Créez la base puis exécutez le schéma SQL décrit dans la section [Base de données](#-base-de-données).

### 4. Configurer Firebase

- Côté **backend** : téléchargez la clé de compte de service depuis la console Firebase
  (_Paramètres du projet → Comptes de service → Générer une nouvelle clé privée_) et placez-la dans
  `backend/serviceAccountKey.json` (ou ailleurs, en renseignant `FIREBASE_CREDENTIALS`).
- Côté **frontend** : renseignez la configuration de votre application web Firebase dans
  `frontend/src/main.js` (objet `firebaseConfig`). En production, `authDomain` pointe sur le domaine
  du site, qui doit alors relayer `/__/auth/` vers `<projet>.firebaseapp.com` et figurer dans les
  _domaines autorisés_ de Firebase Authentication.
- Connexion **Facebook** : l'application Meta doit être en mode _live_, avec l'URI de redirection
  OAuth de Firebase, une politique de confidentialité (`/privacy`) et une page de suppression des
  données (`/data-deletion`) — ces deux pages font partie du front.

> ⚠️ `serviceAccountKey.json` est une clé privée : ne la versionnez pas. Pensez à l'ajouter au `.gitignore`.

---

## 🚀 Démarrage

L'ensemble du projet se lance avec Docker Compose :

```bash
docker compose up --build
```

Le projet est alors accessible sur :

- Frontend : `http://localhost:5173`
- API : `http://localhost:5000`

Un petit script utilitaire affiche également les URLs accessibles depuis un mobile sur le même réseau :

```bash
php start.php
```

### Lancer les services séparément (hors Docker)

**Backend (Flask)**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0
```

**Frontend (Vue + Vite)**

```bash
cd frontend
npm install
npm run dev
```

---

## 🗂️ Architecture

```
.
├── docker-compose.yml       # Orchestration frontend + backend
├── start.php                # Affiche les URLs locales et réseau (accès mobile)
├── backend/
│   ├── app.py               # API Flask : événements, utilisateurs, profils
│   ├── Database.py          # Connexion MySQL (PyMySQL) par contexte de requête
│   ├── await_db.py          # Attend que MySQL réponde avant de démarrer
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── main.js          # Point d'entrée, initialisation Firebase
    │   ├── App.vue          # Layout + navigation (état de connexion)
    │   ├── router/
    │   │   └── index.js     # Routes + garde d'authentification
    │   ├── components/
    │   │   ├── Auth.js      # Synchronisation Firebase ↔ backend
    │   │   └── EventCard.vue
    │   ├── views/
    │   │   ├── Home.vue         # Recherche et liste paginée d'événements
    │   │   ├── EventDetail.vue  # Fiche détaillée d'un événement
    │   │   ├── Register.vue     # Inscription
    │   │   ├── SignIn.vue       # Connexion (email, Google, Facebook)
    │   │   ├── Profile.vue      # Profil utilisateur
    │   │   ├── Privacy.vue      # Politique de confidentialité
    │   │   └── DataDeletion.vue # Suppression des données (exigé par Meta)
    │   └── assets/
    ├── vite.config.js       # Configuration Vite + plugin PWA
    └── Dockerfile
```

---

## ✨ Fonctionnalités

### Recherche d'événements

- Recherche par **ville**, **mot-clé** et **année**
- Filtres avancés : catégorie, nom du lieu, adresse, quartier, code postal, département, région, pays
- Pagination configurable (5, 10, 15 ou 20 événements par page)

### Détail d'un événement

Page dédiée à chaque événement (lieu, adresse, dates, catégorie, mots-clés, description).

### Authentification

- Inscription et connexion par **email / mot de passe**
- Connexion via **Google** et **Facebook**
- Gestion des sessions par Firebase Authentication, jetons vérifiés côté serveur
- Routes protégées côté client (les profils nécessitent d'être connecté)

### Profils utilisateurs

- Création automatique du profil local à la première connexion, avec génération d'un pseudo unique
- Consultation du profil d'un utilisateur par son pseudo
- Modification de sa **bio** et de son **avatar** (uniquement pour son propre profil)
- L'email n'est visible que par le propriétaire du profil

### PWA

Application installable sur mobile et desktop (`vite-plugin-pwa`, mise à jour automatique du service worker).

---

## 🔌 API

Base : `http://localhost:5000`

| Méthode | Route                | Auth | Description                                                     |
| ------- | -------------------- | :--: | --------------------------------------------------------------- |
| `GET`   | `/api/events`        |  –   | Événements à venir (ou de l'année `year`), triés par date, filtrables par `city`, paginés (`rows`, `page`) |
| `GET`   | `/api/events/<uid>`  |  –   | Détail d'un événement par son identifiant OpenAgenda             |
| `POST`  | `/api/users/sync`    |  –   | Crée ou récupère l'utilisateur local à partir d'un jeton Firebase |
| `GET`   | `/api/users/me`      |  ✅  | Informations de l'utilisateur connecté                            |
| `GET`   | `/api/users/<pseudo>`|  ✅  | Profil public d'un utilisateur                                   |
| `PUT`   | `/api/users/<pseudo>`|  ✅  | Mise à jour de sa bio et de son avatar                           |

Les routes marquées ✅ attendent un en-tête `Authorization: Bearer <idToken Firebase>`.

---

## 🗄️ Base de données

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pseudo VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    avatar_url LONGTEXT DEFAULT 'default_avatar.png',
    bio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    is_custom_avatar BOOLEAN DEFAULT FALSE
);

CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    date_start DATETIME NOT NULL,
    date_end DATETIME,
    category VARCHAR(100)
);

CREATE TABLE outings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    organiser_id INT NOT NULL,
    visibility ENUM('public','private') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (organiser_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE participants (
    outing_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (outing_id, user_id),
    FOREIGN KEY (outing_id) REFERENCES outings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    outing_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (outing_id) REFERENCES outings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

> Les tables `outings`, `participants` et `messages` préparent la fonctionnalité de sorties collectives, qui n'est pas encore exposée par l'API (voir [Pistes d'amélioration](#-pistes-damélioration)).

---

## 🧱 Stack technique

| Technologie          | Version    | Usage                                       |
| -------------------- | ---------- | ------------------------------------------- |
| Vue                  | 3.5        | Framework UI                                |
| Vite                 | 7.1        | Build tool & serveur de développement       |
| Vue Router           | 4.5        | Routing client et garde d'authentification  |
| Axios                | 1.11       | Appels HTTP vers l'API                      |
| vite-plugin-pwa      | 1.0        | Service worker et manifest PWA              |
| Firebase (JS SDK)    | 12.2       | Authentification côté client                |
| Flask                | Python 3.12| API REST                                    |
| Flask-CORS           | –          | Autorisation des requêtes cross-origin      |
| firebase-admin       | –          | Vérification des jetons côté serveur        |
| gunicorn             | –          | Serveur WSGI en production                  |
| PyMySQL              | –          | Accès à la base MySQL                       |
| MySQL                | 8.0        | Persistance des utilisateurs                |
| Docker Compose       | –          | Orchestration des services                  |

---

## 🚧 Pistes d'amélioration

- **Sorties collectives** : création d'une sortie autour d'un événement, visibilité publique/privée, gestion des participants et messagerie de groupe (tables déjà présentes dans le schéma)
- Persistance locale des événements consultés (table `events`) plutôt qu'un appel systématique à l'API OpenDataSoft
- Filtrage côté serveur pour l'ensemble des critères avancés (aujourd'hui seuls la ville et l'année le sont, le reste est filtré côté client sur la page courante)
- Externalisation de la configuration Firebase du frontend dans des variables d'environnement
- Suppression de compte depuis l'interface (aujourd'hui sur demande)
- Remplacement des `alert()` par des notifications intégrées à l'interface
- Design plus abouti et responsive, mode hors-ligne réellement exploitable pour la PWA
- Tests automatisés (backend et frontend) et pipeline CI

---

## 👥 Auteurs

- Léa Ballester
- Islem Badaoui
- Gabriel Arman

_Projet réalisé dans le cadre de la Web Academy Epitech Marseille — Promo 2026_
