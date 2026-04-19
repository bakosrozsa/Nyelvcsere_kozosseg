# AI használat dokumentációja

## Nyilatkozat
A fejlesztés során AI-t használtam a követelményelemzés, backend és frontend fejlesztés, hibakeresés, tesztelés és dokumentáció támogatására.

## Források
Az elemzés a következő exportált chat naplók alapján készült:
- `prompts/Chats/chat.json`
- `prompts/Chats/chat2.json`
- `prompts/Chats/chat3.json`

## Felhasználási fázisok
- Követelményelemzés és hiánylisták készítése.
- Backend API és adatmodell fejlesztés (auth, jogosultság, CRUD, validációk).
- Frontend nézetek és route-ok fejlesztése (Login, Register, Dashboard, Mentors, Sessions, Profile).
- Hibakeresés és regresszió-javítás (CORS, import/syntax hibák, role-edge case-ek).
- Tesztek és build/audit ellenőrzések támogatása.
- README és beadási dokumentáció frissítése.

## Jól működő promptok
### 1. Konkrét fájl + konkrét feladat
**Prompt:**
„A backend mappába hozz létre egy `main.py` fájlt, ami egy FastAPI szervert fog megvalósítani.”

**Eredmény:**
Gyorsan használható alap backend jött létre endpointokkal és futtatható szerkezetben.

### 2. Szabály pontosítása üzleti logikára
**Prompt:**
„Értékelni csak befejezett foglalkozásokat lehessen.”

**Eredmény:**
A szabály UI és API oldalon is érvényesítve lett, így csökkent a hibás állapotok esélye.

### 3. Jogosultság és szerepkör alapú viselkedés
**Prompt:**
„Egy diáknak csak a saját foglalkozásait kell látnia, egy mentornak pedig azokat, ahol ő a mentor.”

**Eredmény:**
Pontosan megfogott, ellenőrizhető jogosultsági módosítások készültek.

### 4. Célzott hibajegy bemásolása
**Prompt:**
„[plugin:vite:vue] Unexpected token ... RegisterView.vue”

**Eredmény:**
Gyors szintaktikai hibajavítás történt, és a fordítási hiba megszűnt.

## Kevésbé jól működő promptok
### 1. Túl általános vagy túl tág kérés

### 2. Copilot chat "beakadások"
**Prompt:**
„@agent Try Again”

**Miért volt gyenge:**
Többször előfordult, hogy adott pillanatban a Copilot nem válaszolt/túllépte a válaszidőt(leginkább nagyobb forgalmú időpontokban). Ilyenkor újra felvetetni vele a beszélgetés fonalát nehézkes volt.

### 3. Túl nyitott kérés pontos kontextus nélkül
**Prompt:**
„Mit javítsak még?”

**Miért volt gyenge:**
Konkrét célfájl, hibajegy vagy elvárt kimenet hiányában az eredmény kevésbé célzott.

## Prompt napló összegzés (chat exportok alapján)
### chat.json fő minták
- Alaprendszer felépítése: modellek, adatbázis, FastAPI, auth, JWT, CORS.
- Frontend oldalak és route-ok kialakítása: Login/Register/Home/Dashboard/Mentors/Sessions/Profile.
- Üzleti szabályok iteratív finomítása: foglalás, szerepkörök, mentor profilok, nyelvi célok.

### chat2.json fő minták
- Adatkapcsolati és törlési szabályok pontosítása (cascade).
- Session jogosultsági mátrix szigorítása (ki mit láthat, ki mit módosíthat).
- Foglalási edge case-ek kezelése (önmagához foglalás tiltása, státuszfüggő műveletek).

### chat3.json fő minták
- Követelmény-gap elemzés és prioritások.
- Kritikus/magas/közepes hibák ütemezett javítása.
- Teszt- és build fókusz, valamint dependency/audit jellegű karbantartási lépések.

## Rövid következtetés
Az AI használata akkor volt a leghatékonyabb, amikor a prompt tartalmazta:
- az érintett fájlt vagy modult,
- a pontos üzleti szabályt,
- a kívánt eredményt vagy elfogadási feltételt.

A kevésbé konkrét, túl általános promptoknál több visszakérdezésre volt szükség, és lassabb volt a megoldás.
