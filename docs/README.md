# Nyelvcsere Közösség - Szoftveres dokumentáció

## 1. Projekt célja
A Nyelvcsere Közösség egy teljes web-rendszer, amely nyelvmentorok, nyelvtanulók és látogatók számára biztosít platformot nyelvi cserealkalmak szervezésére, mentorprofilok böngészésére, párosítási javaslatok készítésére és a fejlődés nyomon követésére.

## 2. Használt technológiai stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- JWT alapú hitelesítés
- bcrypt jelszókezelés

### Frontend
- Vue 3
- Vue Router
- Vite
- Axios
- Vitest

### Fejlesztői eszközök
- pytest backend tesztekhez
- GitHub Actions CI
- npm audit / dependency ellenőrzés

## 3. Miért ezeket a technológiákat választottuk?
- A FastAPI gyorsan fejleszthető, jól dokumentált REST API réteget ad.
- Az SQLAlchemy rugalmas ORM megoldás az adatmodellhez.
- Az SQLite egyszerűen futtatható helyben, ezért ideális oktatási projekthez és demóadatokhoz.
- A Vue 3 jó választás egy moduláris, komponens-alapú webalkalmazáshoz.
- A Vite gyors fejlesztői környezetet és build folyamatot biztosít.
- A JWT autentikáció alkalmas arra, hogy a CRUD műveletek csak bejelentkezett felhasználók számára legyenek elérhetők.

## 4. Funkcionális követelmények teljesülése

### 4.1 Hitelesítés és regisztráció
- Regisztráció megvalósítva.
- Bejelentkezés JWT tokennel megvalósítva.
- A CRUD műveletekhez autentikáció szükséges.

### 4.2 CRUD műveletek
- Felhasználók kezelése.
- Mentorprofil kezelés.
- Foglalkozások létrehozása, módosítása és törlése.
- Haladási napló és értékelések kezelése.

### 4.3 Session-kezelés
- Egyéni foglalkozások támogatottak.
- Csoportos foglalkozások támogatottak.
- Csatlakozás és leiratkozás megvalósítva.

### 4.4 Szerepkörök
- Mentor.
- Tanuló.
- Látogató.

### 4.5 Demóadatok
- Az adatbázis induláskor demó nyelveket, felhasználókat, mentorprofilt, sessiont és progress logot tartalmaz.

## 5. Nem-funkcionális követelmények teljesülése
- A backend REST API-t biztosít.
- A frontend HTTP kérésekkel kommunikál a szerverrel.
- A rendszer lokálisan futtatható.
- A projekt tartalmaz automatizált teszteket.
- A CI pipeline ellenőrzi a backend és frontend részeket.
- A kód dokumentált és környezeti változókkal konfigurálható.

## 6. Adatmodell
Az adatmodell fő entitásai:
- users
- languages
- mentor_profiles
- sessions
- session_participants
- progress_logs
- session_evaluations

## 7. Példa demóadatok

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

## 8. Telepítés és futtatás
A részletes telepítési és futtatási utasítások a gyökér README-ben és a frontend README-ben találhatók.

## 9. Megjegyzés
Ez a dokumentáció mintastruktúra a beadási követelményekhez igazodik. A végleges változatban érdemes mellé tenni képernyőképeket, API példákat és rövid architektúra-ábrát is.
