# AI használat dokumentációja

## Nyilatkozat
A fejlesztés során AI-t használtam követelményelemzéshez, backend és frontend fejlesztéshez, hibakereséshez, tesztelési ellenőrzésekhez és a beadási dokumentációk karbantartásához.

## Források
Az összegzés az exportált chat naplókra épül:
- `prompts/Chats/chat.json`
- `prompts/Chats/chat2.json`
- `prompts/Chats/chat3.json`

## Felhasználási fázisok
- Követelmények bontása és hiánylisták készítése.
- Backend API, adatmodell és üzleti szabályok kialakítása.
- Frontend nézetek, route-ok és auth-élmény finomítása.
- Hibakeresés és regressziók javítása a backendben és frontendben.
- Tesztek, build és CI-ellenőrzések támogatása.
- A jelenlegi technikai dokumentációk frissítése a kódbázis tényleges állapota szerint.

## Jól működő promptok
### 1. Konkrét fájl + konkrét feladat
**Prompt:**
„A backend mappába hozz létre egy `main.py` fájlt, ami egy FastAPI szervert fog megvalósítani.”

**Eredmény:**
Gyorsan használható API-váz jött létre endpointokkal és futtatható szerkezettel.

### 2. Üzleti szabály pontosítása
**Prompt:**
„Értékelni csak befejezett foglalkozásokat lehessen.”

**Eredmény:**
A szabály a backendben és a frontend viselkedésében is érvényesíthető lett.

### 3. Szerepkör-alapú viselkedés
**Prompt:**
„Egy diáknak csak a saját foglalkozásait kell látnia, egy mentornak pedig azokat, ahol ő a mentor.”

**Eredmény:**
Jól célzott, ellenőrizhető jogosultsági finomítások készültek.

### 4. Célzott hibajegy bemásolása
**Prompt:**
„[plugin:vite:vue] Unexpected token ... RegisterView.vue”

**Eredmény:**
Gyors szintaktikai hibajavítás történt, és a build hiba megszűnt.

## Kevésbé jól működő promptok
### 1. Túl általános kérés

### 2. Copilot chat újrapróbálás
**Prompt:**
„@agent Try Again”

**Miért volt gyenge:**
Többször előfordult, hogy adott pillanatban a Copilot nem válaszolt/túllépte a válaszidőt(leginkább nagyobb forgalmú időpontokban). Ilyenkor újra felvetetni vele a beszélgetés fonalát nehézkes volt.

### 3. Túl nyitott kérés pontos cél nélkül
**Prompt:**
„Mit javítsak még?”

**Miért volt gyenge:**
Fájl, hiba vagy elfogadási feltétel hiányában a válaszok kevésbé voltak célzottak.

## Prompt napló összegzés (chat exportok alapján)
### chat.json fő minták
- Alaprendszer felépítése: modellek, adatbázis, FastAPI, auth, JWT és CORS.
- Frontend oldalak és route-ok kialakítása: Home, Login, Register, Mentors, Dashboard, Sessions, Profile.
- Foglalási és mentorprofil logika iteratív finomítása.

### chat2.json fő minták
- Adatkapcsolati és törlési szabályok pontosítása.
- Session jogosultsági mátrix szigorítása.
- Foglalási edge case-ek kezelése, például az önfoglalás tiltása.

### chat3.json fő minták
- Követelmény-gap elemzés és prioritások.
- Kritikus, magas és közepes hibák javítása.
- Teszt- és build-fókuszú karbantartási lépések.

## Rövid következtetés
Az AI a leghatékonyabb akkor volt, amikor a prompt tartalmazta:
- az érintett fájlt vagy modult,
- a konkrét üzleti szabályt,
- a kívánt viselkedést vagy elfogadási feltételt.

Az általános, kontextus nélküli promptoknál több visszakérdezésre volt szükség, és lassabb volt a megoldás.
