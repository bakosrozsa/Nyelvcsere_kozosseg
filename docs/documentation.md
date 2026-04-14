# Nyelvcsere Közösség - Szoftveres dokumentáció

## 1. Projekt célja
A Nyelvcsere Közösség egy teljes web-rendszer, amely nyelvmentorok, nyelvtanulók és látogatók számára biztosít platformot nyelvi cserealkalmak szervezésére, mentorprofilok böngészésére, párosítási javaslatok készítésére és a fejlődés nyomon követésére.

## 2. Állapot

Last updated: April 14, 2026

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

## 3. Használt technológiai stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- JWT alapú hitelesítés (`python-jose`)
- bcrypt jelszókezelés (`passlib`)
- Uvicorn

### Frontend
- Vue 3 (Composition API)
- Vue Router
- Vite
- Axios
- CSS (custom dark theme)
- Vitest

### Fejlesztői eszközök
- pytest backend tesztekhez
- GitHub Actions CI
- npm audit/dependency ellenőrzés

## 4. Miért ezeket a technológiákat választottam?
- A FastAPI gyorsan fejleszthető, jól dokumentált REST API réteget ad.
- Az SQLAlchemy rugalmas ORM megoldás az adatmodellhez.
- Az SQLite egyszerűen futtatható helyben, ezért ideális oktatási projekthez és demóadatokhoz.
- A Vue 3 jó választás egy moduláris, komponens-alapú webalkalmazáshoz.
- A Vite gyors fejlesztői környezetet és build folyamatot biztosít.
- A JWT autentikáció alkalmas arra, hogy a CRUD műveletek csak bejelentkezett felhasználók számára legyenek elérhetők.

## 5. Funkcionális követelmények teljesülése

### 5.1 Hitelesítés és regisztráció
- Regisztráció megvalósítva.
- Bejelentkezés JWT tokennel megvalósítva.
- A CRUD műveletekhez autentikáció szükséges.

### 5.2 CRUD műveletek
- Felhasználók kezelése.
- Mentorprofil kezelés.
- Foglalkozások létrehozása, módosítása és törlése.
- Haladási napló és értékelések kezelése.

### 5.3 Session-kezelés
- Egyéni foglalkozások támogatottak.
- Csoportos foglalkozások támogatottak.
- Csatlakozás és leiratkozás megvalósítva.

### 5.4 Szerepkörök
- Mentor.
- Tanuló.
- Látogató.

### 5.5 Demóadatok
- Az adatbázis induláskor demó nyelveket, felhasználókat, mentorprofilt, sessiont és progress logot tartalmaz.

## 6. Nem-funkcionális követelmények teljesülése
- A backend REST API-t biztosít.
- A frontend HTTP kérésekkel kommunikál a szerverrel.
- A rendszer lokálisan futtatható.
- A projekt tartalmaz automatizált teszteket.
- A CI pipeline ellenőrzi a backend és frontend részeket.
- A kód dokumentált és környezeti változókkal konfigurálható.

## 7. Projekt struktúra

```text
Nyelvcsere_kozosseg/
|-- backend/
|   |-- database.py
|   |-- init_db.py
|   |-- main.py
|   `-- models.py
|-- docs/
|   `-- documentation.md
|-- frontend/
|   |-- package.json
|   |-- vite.config.js
|   |-- index.html
|   `-- src/
|       |-- App.vue
|       |-- main.js
|       |-- style.css
|       |-- router/index.js
|       `-- views/
|           |-- HomeView.vue
|           |-- LoginView.vue
|           |-- RegisterView.vue
|           |-- DashboardView.vue
|           |-- MentorsView.vue
|           |-- SessionsView.vue
|           |-- ProfileView.vue
|           `-- NotFoundView.vue
|-- prompts/
`-- README.md
```

## 8. Adatmodell
Az adatmodell fő entitásai:
- users
- languages
- mentor_profiles
- sessions
- session_participants
- progress_logs
- session_evaluations

## 9. Példa demóadatok

### Felhasználók
- `anna.mentor@example.com` - mentor
- `peter.student@example.com` - tanuló

### Nyelvek
- English
- Hungarian
- German

### Példa mentorprofil
- Tanított nyelv: English
- Tanult nyelv: Hungarian
- Foglalkozás hossza: 60 perc

### Példa session
- Időpont: a következő napra ütemezett foglalkozás
- Státusz: scheduled

## 10. Telepítés és futtatás

### 10.1 Backend
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

### 10.2 Frontend előfeltételek
- Node.js 20.19+ (vagy 22.12+)
- Futó backend API (alapértelmezés: `http://127.0.0.1:8000`)

### 10.3 Frontend környezeti változók
Hozz létre `frontend/.env` fájlt a `frontend/.env.example` alapján:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 10.4 Frontend fejlesztés
```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

### 10.5 Frontend build
```bash
cd frontend
npm run build
npm run preview
```

### 10.6 Tesztelés

Backend smoke tesztek:
```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

Frontend tesztek:
```bash
cd frontend
npm run test
```

## 11. API összefoglaló

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

## 12. Frontend route-ok
- `/` - Kezdőoldal
- `/login` - Bejelentkezés
- `/register` - Regisztráció
- `/mentors` - Mentorlista
- `/profile` - Profil
- `/sessions` - Foglalkozások
- `/dashboard` - Dashboard

## 13. Kiegészítő dokumentumok
- AI-használat összegzése: `prompts/README.md`
- Prompt napló: `prompts/prompt-log.md`

## 14. Megjegyzés
`init_db.py` futtatása újraépíti a demo adatbázist. Ha teljes reset kell, töröld a `backend/nyelvcsere.db` fájlt és futtasd újra az initet.

