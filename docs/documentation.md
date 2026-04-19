# Nyelvcsere Közösség – Technikai dokumentáció

## 1. Projekt célja

A Nyelvcsere Közösség egy teljes webes platform, amely nyelvmentorok, nyelvtanulók és látogatók számára biztosít lehetőséget nyelvi cserealkalmak szervezésére, mentorprofilok böngészésére, párosítási javaslatok készítésére és a fejlődés nyomon követésére.

---

## 2. Állapot

Last updated: April 19, 2026

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

---

## 3. Technológiai stack és döntések indoklása

### 3.1 Backend

| Csomag | Megjegyzés |
|--------|------------|
| FastAPI | REST API réteg |
| SQLAlchemy | ORM |
| SQLite | Adatbázis (helyi/demó) |
| python-jose | JWT hitelesítés |
| passlib + bcrypt | Jelszókezelés |
| Uvicorn | ASGI szerver |

#### FastAPI
- Automatikus OpenAPI/Swagger dokumentáció generálás, amely megkönnyíti a fejlesztést és a tesztelést.
- Natív aszinkron támogatás (`async/await`), ami jobb teljesítményt nyújt I/O-intenzív műveleteknél.
- Python típusannotációkon alapuló validáció (Pydantic), így a bemeneti adatok ellenőrzése kódszinten megoldott.
- Minimális boilerplate-tel készíthető működő API, ami oktatási és demójellegű projektekhez különösen alkalmas.

#### SQLAlchemy
- Rugalmas, adatbázisfüggetlen ORM: az SQLite szükség esetén könnyen cserélhető PostgreSQL-re.
- Deklaratív modell-definíció, amely átlátható adatmodellt eredményez.
- Alembic-kel bővíthető migráció-támogatás.

#### SQLite
- Telepítés nélkül, egyetlen fájlként futtatható, ami helyi fejlesztéshez és demóadatokhoz ideális.
- **Fontos korlát:** SQLite nem alkalmas éles, nagy terhelésű, többfelhasználós környezetbe. Párhuzamos írási műveleteknél zárolási problémák léphetnek fel. Éles rendszernél PostgreSQL-re való csere javasolt, de ez túlhaladja a beadandót.

#### JWT + bcrypt
- A JWT (JSON Web Token) állapotmentes hitelesítést tesz lehetővé: a szerver nem tárol munkamenet-adatot, a token maga tartalmazza a szükséges információkat. A tokenek lejárati idővel rendelkeznek.
- A bcrypt iparági szabványnak megfelelő jelszóhashing algoritmust biztosít: sózott, lassított hash, amely ellenáll brute-force támadásoknak.

---

### 3.2 Frontend

| Csomag | Megjegyzés |
|--------|------------|
| Vue 3 (Composition API) | UI keretrendszer |
| Vue Router | Oldalnavigáció |
| Vite | Fejlesztői szerver és build |
| Axios | HTTP kliens |
| CSS (custom dark theme) | Glassmorphism UI téma |
| Vitest | Frontend tesztek |

#### Vue 3
- Komponens-alapú architektúra, amely modulárissá és újrafelhasználhatóvá teszi a kódot.
- A Composition API tisztább, típusbarát kódszervezést tesz lehetővé az Options API-val szemben.

#### Vite
- Natív ES modulokat használó, rendkívül gyors fejlesztői szerver Hot Module Replacement (HMR) támogatással.

#### Axios
- Promise-alapú HTTP kliens; interceptorok segítségével a JWT token automatikusan csatolható minden kéréshez.

---

### 3.3 Fejlesztői eszközök

- **pytest** – Python ökoszisztéma de facto standard tesztelési keretrendszere; jól integrálható a FastAPI `TestClient`-tel.
- **GitHub Actions CI** – Minden push és pull request esetén automatikusan futtatja a backend és frontend teszteket.
- **npm audit** – Automatikus függőség-biztonsági ellenőrzés a frontend csomagokra.

---

## 4. Funkcionális követelmények teljesülése

### 4.1 Hitelesítés és regisztráció
- Felhasználói regisztráció e-mail és jelszó alapján megvalósítva.
- Bejelentkezés JWT token kiadásával; a token a védett végpontokhoz szükséges.
- Minden CRUD műveletet autentikációhoz kötöttük: autentikáció nélküli kérések 401-es hibával visszautasítottak.

### 4.2 CRUD műveletek
- **Felhasználók:** létrehozás, lekérdezés, módosítás, törlés.
- **Mentorprofilok:** létrehozás, szerkesztés, törlés; nyilvános lekérdezés látogatók számára is elérhető.
- **Foglalkozások:** létrehozás, módosítás, törlés, résztvevők kezelése.
- **Haladási napló:** bejegyzések hozzáadása és lekérdezése.
- **Értékelések:** foglalkozás utáni értékelések létrehozása és megtekintése.

### 4.3 Session-kezelés
- Egyéni (1:1) és csoportos foglalkozások támogatottak (`max_students`: 2–10).
- Felhasználók csatlakozhatnak meglévő foglalkozáshoz, illetve le is iratkozhatnak róla.
- Foglalkozások státusza nyomon követhető: `scheduled`, `completed`, `canceled`.

### 4.4 Szerepkörök

| Szerepkör | Leírás |
|-----------|--------|
| Mentor | Foglalkozásokat hirdet, profilt kezel, értékeléseket kap, párosítási javaslatokat lát |
| Tanuló | Foglalkozásokra jelentkezik, haladást naplóz, értékel |
| Látogató | Mentorprofilokat és nyilvános foglalkozásokat böngész regisztráció nélkül |

### 4.5 Demóadatok
Az adatbázis induláskor automatikusan feltöltésre kerül:
- Nyelvek: English, Hungarian, German
- Felhasználók: `anna.mentor@example.com` (mentor), `peter.student@example.com` (tanuló)
- Minta mentorprofil (tanított: English, tanult: Hungarian, 60 perc), foglalkozás (`scheduled`) és progress log bejegyzés

---

## 5. Nem-funkcionális követelmények teljesülése

### 5.1 Biztonság
- Jelszavak bcrypt-tel hashelve tárolódnak; plain-text jelszó soha nem kerül adatbázisba.
- JWT tokenek lejárati idővel rendelkeznek, csökkentve a kompromittált token kockázatát.
- Védett végpontok autentikáció nélkül nem érhetők el.
- Frontend függőségek biztonsági auditja automatizált (`npm audit`).

### 5.2 Architektúra és integráció
- A backend tiszta REST API-t biztosít; a frontend kizárólag HTTP kéréseken keresztül kommunikál a szerverrel – a rétegek egymástól függetlenek.
- A rendszer bármilyen operációs rendszeren futtatható helyileg, külső infrastruktúra nélkül.

### 5.3 Tesztelhetőség és CI/CD
- Backend pytest-tel tesztelve, frontend Vitest-tel.
- GitHub Actions CI pipeline minden módosításnál automatikusan futtatja a teszteket.

### 5.4 Karbantarthatóság és konfiguráció
- A kód modulárisan szervezett, a backend és frontend egymástól elkülönített könyvtárakban.
- Konfigurálható környezeti változókkal (`SECRET_KEY`, adatbázis elérési út, CORS, `VITE_API_BASE_URL`).

### 5.5 Teljesítmény
- A FastAPI aszinkron kezelése alacsony látogatottságú, oktatási jellegű projekthez megfelelő teljesítményt nyújt.
- Magasabb terhelés esetén az SQLite lecserélése PostgreSQL-re javasolt.

---

## 6. Projekt struktúra

```text
Nyelvcsere_kozosseg/
├── backend/
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   └── models.py
├── docs/
│   └── documentation.md
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
├── prompts/
└── README.md
```

---

## 7. Adatmodell

| Entitás | Leírás |
|---------|--------|
| `users` | Regisztrált felhasználók (mentor, tanuló, látogató) |
| `languages` | Elérhető nyelvek |
| `mentor_profiles` | Mentorok profilja, tanított/tanult nyelvek, elérhetőség |
| `sessions` | Szervezett foglalkozások (időpont, típus, státusz) |
| `session_participants` | Foglalkozás–felhasználó kapcsolótábla |
| `progress_logs` | Tanulók haladási naplóbejegyzései (`rating`, `notes`) |
| `session_evaluations` | Foglalkozások utáni értékelések |

---

## 8. Telepítés és futtatás

### 8.1 Backend

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

### 8.2 Frontend előfeltételek
- Node.js 20.19+ (vagy 22.12+)
- Futó backend API (alapértelmezés: `http://127.0.0.1:8000`)

### 8.3 Frontend környezeti változók

Hozz létre `frontend/.env` fájlt a `frontend/.env.example` alapján:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 8.4 Frontend fejlesztés

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

### 8.5 Frontend build

```bash
cd frontend
npm run build
npm run preview
```

### 8.6 Tesztelés

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

---

## 9. API összefoglaló

### Auth és felhasználók
- `POST /register`
- `POST /login`
- `GET /token-check`
- `GET /users` (mentor: teljes lista; student: csak a többi tanuló, saját magát és mentorokat nem tartalmazza)
- `GET /users/me`
- `PUT /users/me`
- `GET /users/{user_id}`
- `GET /public/mentor-users` (vendég módban is elérhető mentorlista)

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

Megjegyzés az értékeléshez: egy mentor alapértelmezetten csak egyszer menthet értékelést tanulónként adott foglalkozáshoz. Már mentett értékelés módosításához a kérésben `allow_update=true` szükséges.

---

## 10. Frontend route-ok

| Route | Oldal |
|-------|-------|
| `/` | Kezdőoldal |
| `/login` | Bejelentkezés |
| `/register` | Regisztráció |
| `/mentors` | Mentorlista |
| `/profile` | Profil |
| `/sessions` | Foglalkozások |
| `/dashboard` | Dashboard |

---

## 11. Kiegészítő dokumentumok
- AI-használat összegzése: `prompts/README.md`
- Prompt napló: `prompts/prompt-log.md`

---

## 12. Megjegyzés

`init_db.py` futtatása újraépíti a demó adatbázist. Ha teljes reset kell, töröld a `backend/nyelvcsere.db` fájlt és futtasd újra az initet.