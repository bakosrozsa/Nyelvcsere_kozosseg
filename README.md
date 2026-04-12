# Nyelvcsere Közösség

Nyelvcsere platform mentoroknak és tanulóknak, FastAPI backenddel és Vue 3 front-enddel.

## Állapot

**Last updated:** April 3, 2026

Fő funkciók:
- JWT alapú autentikáció és jogosultságkezelés (`student`, `mentor`)
- Vendég mód: mentorlista megtekinthető bejelentkezés nélkül
- Mentor profil kezelés (tanított/tanult nyelv, időtartam, elérhetőség, cserefeltételek)
- 1:1 és csoportos foglalkozások
- Csoportos foglalkozás korlát: `max_students` csak 2 és 10 között
- Csoportos csatlakozás és lejelentkezés
- Session státuszkezelés (`scheduled`, `completed`, `canceled`)
- Haladási napló (`rating`, `notes`) és foglalkozás utáni értékelési folyamat
- Mentor oldali párosítási javaslatok (csak diákokra)
- Dashboard: felhasználók, párosítások, erőforrások
- App-szintű sötét/glassmorphism UI téma (konzisztens kártya stílusok)

## Tech stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- JWT (`python-jose`), bcrypt (`passlib`)
- Uvicorn

### Frontend
- Vue 3 (Composition API)
- Vue Router
- Vite
- CSS (custom dark theme)

## Projekt struktúra

```text
Nyelvcsere_kozosseg/
├── backend/
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   └── models.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── style.css
│       ├── router/index.js
│       └── views/
│           ├── HomeView.vue
│           ├── LoginView.vue
│           ├── RegisterView.vue
│           ├── DashboardView.vue
│           ├── MentorsView.vue
│           ├── SessionsView.vue
│           ├── ProfileView.vue
│           └── NotFoundView.vue
└── README.md
```

## Kiegészítő dokumentáció

- [docs/README.md](docs/README.md) - részletes szoftveres dokumentáció
- [prompts/README.md](prompts/README.md) - AI-használat összegzése
- [prompts/prompt-log.md](prompts/prompt-log.md) - minta promptnapló

## Gyors indítás

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
set NYELVCSERE_SECRET_KEY=replace-with-a-long-random-secret
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

Tipp: a `backend/.env.example` fájl mintát ad a szükséges környezeti változókhoz.

Backend URL: `http://127.0.0.1:8000`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend fejlesztéshez ajánlott Node verzió: `22.12.0` (minimum: `20.19.0`).

Ha nem alapértelmezett backend címet használsz, hozz létre `frontend/.env` fájlt a `frontend/.env.example` alapján, és állítsd be a `VITE_API_BASE_URL` értékét.

Frontend URL: `http://localhost:5173`

## Tesztelés

Backend smoke tesztek futtatása:

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

## API összefoglaló

### Auth és felhasználók
- `POST /register`
- `POST /login`
- `GET /token-check`
- `GET /users` (mentor: teljes lista, student: saját profil)
- `GET /users/me`
- `PUT /users/me`
- `GET /users/{user_id}`
- `GET /public/mentor-users` (vendég módban is elérhető mentorlista adat)

### Nyelvek és mentor profilok
- `GET /languages`
- `GET /mentor-profiles`
- `GET /mentor-profile/me`
- `PUT /mentor-profile/me`

### Párosítás és erőforrások
- `GET /pairing-suggestions`
- `GET /mentor-pairing-groups`
- `GET /mentor-resources`
- `GET /community-interactions`

### Foglalkozások
- `GET /sessions`
- `POST /sessions`
- `PUT /sessions/{session_id}`
- `DELETE /sessions/{session_id}`
- `GET /sessions/group-available`
- `POST /sessions/{session_id}/join`
- `DELETE /sessions/{session_id}/leave`
- `GET /sessions/{session_id}/participants`
- `GET /sessions/{session_id}/progress-log`
- `PUT /sessions/{session_id}/progress-log`
- `GET /sessions/{session_id}/evaluations`
- `PUT /sessions/{session_id}/evaluations/{student_id}`

## Frontend route-ok

- `/` - Kezdőoldal
- `/login` - Bejelentkezés
- `/register` - Regisztráció
- `/mentors` - Mentorlista
- `/profile` - Profil
- `/sessions` - Foglalkozások
- `/dashboard` - Dashboard

## Megjegyzés

`init_db.py` futtatása újraépíti a demo adatbázist. Ha teljes reset kell, töröld a `backend/nyelvcsere.db` fájlt és futtasd újra az initet.
