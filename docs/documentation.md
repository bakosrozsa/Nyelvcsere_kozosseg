# Nyelvcsere Közösség – Technikai dokumentáció

## 1. Projekt célja

A Nyelvcsere Közösség egy webes nyelvcsere-platform, amely összehozza a tanulókat és mentorokat. A rendszer támogatja a mentorprofilok böngészését, a nyelvi párosítási javaslatokat, az egyéni és csoportos foglalkozások kezelését, valamint a haladás és értékelések nyomon követését.

---

## 2. Állapot

Last updated: May 3, 2026

Fő funkciók:
- JWT-alapú autentikáció és szerepkör-kezelés (`student`, `mentor`)
- Vendég mód: a kezdőoldal és a mentorlista bejelentkezés nélkül is elérhető
- Mentorprofil-kezelés tanított és tanult nyelvvel, időtartammal, elérhetőséggel és cserefeltételekkel
- Egyéni foglalás diákoknak, csoportos foglalkozás mentoroknak
- Csoportos foglalkozás-kapacitás: `max_students` csak 2 és 10 között lehet
- Csoportos csatlakozás és leiratkozás diákoknak
- Session státuszok: `scheduled`, `completed`, `canceled`
- Haladási napló (`notes`, `rating`) és foglalkozás utáni értékelés
- Mentor-only párosítási javaslatok és mentorcsoportok
- Mentor-only erőforráslista és közösségi összefoglaló
- Felhasználói dashboard, profiloldal és foglalkozáskezelés a frontendben
- Modern, sötét, glassmorphism jellegű UI a Vue alkalmazásban

---

## 3. Technológiai stack és döntések indoklása

### 3.1 Backend

| Csomag | Verzió | Megjegyzés |
|--------|--------|------------|
| FastAPI | 0.136.1 | REST API réteg, OpenAPI dokumentációval |
| Uvicorn | 0.34.0 | ASGI szerver |
| SQLAlchemy | 2.0.39 | ORM |
| Pydantic | 2.11.1 | Modell- és validációs réteg |
| python-jose | 3.5.0 | JWT hitelesítés |
| bcrypt | 4.3.0 | Jelszóhashing |
| SQLite | beépített | Helyi és demó adatbázis |

#### FastAPI
- Automatikus OpenAPI/Swagger dokumentációt ad.
- Típusannotációkra és Pydantic modellekre épül, ezért a request/response validáció erős.
- Egyszerűen olvasható, kevés boilerplate-tel írható API-t ad.

#### SQLAlchemy
- Átlátható ORM-megoldás, amely a schema- és query-logikát külön kezeli.
- A jelenlegi SQLite háttér később könnyen cserélhető más relációs adatbázisra.

#### SQLite
- Egyszerű, fájlalapú tárolás a helyi fejlesztéshez és a seedelt demóhoz.
- Többfelhasználós, nagy terhelésű éles környezetben nem ideális, ezért a dokumentáció és a kód is lokális/demó használatra van optimalizálva.

#### JWT + bcrypt
- A JWT állapotmentes hitelesítést biztosít.
- A bcrypt lassított hash-t használ, így a jelszavak nem nyers formában kerülnek tárolásra.

### 3.2 Frontend

| Csomag | Verzió | Megjegyzés |
|--------|--------|------------|
| Vue | 3.5.30 | UI keretrendszer |
| Vue Router | 5.0.4 | Oldalnavigáció |
| Vite | 8.0.3 | Dev server és build |
| Axios | 1.13.6 | HTTP kliens |
| Vitest | 4.1.2 | Frontend tesztek |

#### Vue 3
- Komponens-alapú struktúra, jól elkülönített nézetekkel.
- A Composition API jól illeszkedik a kisebb, önálló funkciókra bontott oldalstruktúrához.

#### Vite
- Gyors fejlesztői környezet és build folyamat.

#### Axios
- A foglalkozás- és felhasználói lekérésekhez használt HTTP kliens a frontendben.

### 3.3 Fejlesztői eszközök

- pytest – backend smoke tesztekhez.
- GitHub Actions CI – a backend teszteket, a frontend teszteket és a buildet automatikusan futtatja.
- npm audit – a frontend függőségek biztonsági ellenőrzéséhez.

---

## 4. Funkcionális követelmények teljesülése

### 4.1 Hitelesítés és regisztráció
- Regisztráció e-mail, jelszó és szerepkör alapján működik.
- Bejelentkezéskor JWT token keletkezik.
- A védett API-végpontok token nélkül 401 választ adnak.
- A frontend a token alapján kezeli a menüpontok és oldalak láthatóságát.

### 4.2 Felhasználó- és profilkezelés
- A felhasználók saját adataikat módosíthatják a `users/me` végponton.
- A mentoroknak automatikusan létrejön mentorprofil, és azt a `mentor-profile/me` végponttal módosíthatják.
- A mentoroknak külön nyilvános listájuk van, amely vendégként is böngészhető.

### 4.3 Párosítás és közösségi funkciók
- A rendszer mentorok számára párosítási javaslatokat generál a nyelvi célok alapján.
- A mentorok mentorcsoportokat is látnak, amelyek azonos mentorhoz tartozó találatokat gyűjtik össze.
- A mentorok számára elérhetők erőforrások és közösségi összefoglalók.

### 4.4 Foglalkozások és session-kezelés
- A diákok egyéni foglalkozást hozhatnak létre.
- A mentorok csoportos foglalkozást hozhatnak létre a saját profiljukhoz.
- A diákok csoportos foglalkozásokhoz csatlakozhatnak és onnan leiratkozhatnak.
- A mentorok módosíthatják a foglalkozás státuszát, illetve a még `scheduled` állapotú időpontot.
- Az értékelések és a haladási naplók csak befejezett foglalkozásokhoz írhatók, és a meglévő bejegyzések módosítása külön engedélyt kér (`allow_update=true`).

### 4.5 Szerepkörök

| Szerepkör | Leírás |
|-----------|--------|
| Mentor | Mentorprofilt kezel, csoportos foglalkozást hoz létre, párosítási javaslatokat és erőforrásokat lát, valamint értékeléseket rögzít |
| Tanuló | Egyéni foglalkozást foglal, csoportos foglalkozáshoz csatlakozik, saját haladását és értékeléseit követi |
| Vendég | Kezdőoldalt és mentorlistát nézhet bejelentkezés nélkül |

### 4.6 Demóadatok
Az adatbázis induláskor automatikusan feltöltődik a következőkkel:
- Nyelvek: English, Hungarian, German
- Felhasználók: `anna.mentor@example.com` (mentor) és `peter.student@example.com` (tanuló)
- Minta mentorprofil: English tanítása, Hungarian tanulása, 60 perces foglalkozás
- Minta egyéni foglalkozás és progress log bejegyzés

---

## 5. Nem-funkcionális követelmények teljesülése

### 5.1 Biztonság
- A jelszavak bcrypt-tel hashelve tárolódnak.
- A tokenek lejárati idővel rendelkeznek.
- A szerepkör-alapú végpontvédelem a backendben van kikényszerítve.
- A frontend dependency-audit a CI részét is képezi.

### 5.2 Architektúra és integráció
- A backend tiszta REST API-t ad, a frontend pedig HTTP kérésekkel kapcsolódik hozzá.
- A backend és frontend külön könyvtárban van, külön build- és futtatási lépésekkel.
- A rendszer lokálisan Docker Compose-zal is futtatható.

### 5.3 Tesztelhetőség és CI/CD
- A backend smoke tesztek pytest-tel futnak.
- A frontend tesztek Vitest-tel futnak.
- A GitHub Actions workflow push és pull request esetén futtatja a backend teszteket, a frontend teszteket és a frontend buildet.

### 5.4 Karbantarthatóság és konfiguráció
- A konfiguráció környezeti változókon keresztül történik, például `NYELVCSERE_SECRET_KEY`, `NYELVCSERE_TIMEZONE` és `VITE_API_BASE_URL`.
- A seedelés külön `init_db.py` fájlban van kezelve.

### 5.5 Teljesítmény
- A jelenlegi implementáció oktatási és demó célra van optimalizálva.
- Nagyobb terhelésre PostgreSQL-alapú háttértár lenne célszerű.

---

## 6. Projekt struktúra

```text
Nyelvcsere_kozosseg/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── tests/
│       └── test_api_smoke.py
├── docs/
│   └── documentation.md
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── style.css
│       ├── config/
│       ├── router/
│       ├── utils/
│       └── views/
└── prompts/
	├── ai_documentation.md
	└── Chats/
		├── chat.json
		├── chat2.json
		└── chat3.json
```

---

## 7. Adatmodell

| Entitás | Leírás |
|---------|--------|
| `users` | Regisztrált felhasználók mentor vagy tanuló szerepkörrel |
| `languages` | Elérhető nyelvek |
| `mentor_profiles` | Mentorok profiladatai, nyelvpárok és elérhetőség |
| `sessions` | Egyéni vagy csoportos foglalkozások |
| `session_participants` | Csoportos foglalkozások résztvevői |
| `progress_logs` | Haladási naplóbejegyzések |
| `session_evaluations` | Mentorértékelések foglalkozásonként és tanulónként |

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

Tipp: a `backend/.env.example` fájl a szükséges környezeti változók mintáját tartalmazza.

Backend URL: `http://127.0.0.1:8000`

### 8.2 Frontend előfeltételek
- Node.js 20.19+ vagy 22.12+
- Futó backend API `http://127.0.0.1:8000` címen

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

### 8.7 Konténeres futtatás (Docker Compose)

Előfeltétel: telepített Docker Desktop Compose támogatással.

Projekt gyökeréből indítás:

```bash
docker compose up --build
```

Elérhető URL-ek:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend OpenAPI: `http://localhost:8000/docs`

Háttérben indítás:

```bash
docker compose up --build -d
```

Logok megtekintése:

```bash
docker compose logs -f
```

Leállítás:

```bash
docker compose down
```

Adatok teljes törlése:

```bash
docker compose down -v
```

---

## 9. API összefoglaló

### Általános
- `GET /` – backend állapotüzenet
- `GET /health` – egészségellenőrzés

### Auth és felhasználók
- `POST /register`
- `POST /login`
- `GET /token-check`
- `GET /users` – mentor: teljes lista, student: csak más tanulók
- `GET /users/me`
- `PUT /users/me`
- `GET /users/{user_id}`
- `GET /public/mentor-users` – nyilvános mentorlista

### Nyelvek és mentorprofilok
- `GET /languages`
- `GET /mentor-profiles`
- `GET /mentor-profile/me`
- `PUT /mentor-profile/me`

### Párosítás és mentor eszközök
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

Megjegyzés: a már létező értékelések és progress logok módosításához a kérésben `allow_update=true` szükséges.

---

## 10. Frontend route-ok

| Route | Oldal |
|-------|-------|
| `/` | Kezdőoldal |
| `/login` | Bejelentkezés |
| `/register` | Regisztráció |
| `/mentors` | Mentorlista |
| `/dashboard` | Felhasználók |
| `/profile` | Profil |
| `/sessions` | Foglalkozások |
| `/:pathMatch(.*)*` | 404 oldal |

---

## 11. Kiegészítő dokumentumok
- AI-használat összegzése: `prompts/ai_documentation.md`
- Exportált chat naplók: `prompts/Chats/chat.json`, `prompts/Chats/chat2.json`, `prompts/Chats/chat3.json`

---

## 12. Megjegyzés

Lokális, nem Dockeres futtatásnál az `init_db.py` újraépíti a demó adatbázist. Ha teljes reset kell, töröld a `backend/nyelvcsere.db` fájlt, majd futtasd újra az initet. Dockeres futtatásnál ugyanez a `docker compose down -v` paranccsal érhető el.