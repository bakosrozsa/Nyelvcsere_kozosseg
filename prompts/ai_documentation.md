# AI használat dokumentációja

## Nyilatkozat
A fejlesztés során AI-t használtam a tervezés, a hibakeresés, a dokumentációs szövegek és a tesztek finomításának támogatására.

## Összegzés
### Jól működő promptok
- „Mondd el, a projekt leírása alapján mely funkciók hiányoznak még, és melyek prioritásosak.”
- „Javítsd úgy a backend autentikációt, hogy a CRUD végpontok csak hitelesített felhasználóknak legyenek elérhetők.”
- „Készíts rövid, beadásra alkalmas dokumentációs vázlatot a technológiai stackről és a teljesített követelményekről.”
- „Készíts teszttervet a backend smoke tesztekhez.”

### Kevésbé jól működő promptok
- Túl általános kérdés: „Mit javítsak még?”
- Konkrét fájlok vagy követelmények nélküli promptok.
- Túl tág utasítás: „Mindent javíts ki.”

## Felhasználási fázisok
- Követelményelemzés
- Architektúra és API tervezés
- Hibaelhárítás
- Dokumentációírás
- Tesztelési ötletek kidolgozása

## Prompt napló - minta

### 1. Követelményelemzés
**Prompt:**
Mondd el, a projekt leírása alapján mely funkciók hiányoznak még, és melyek prioritásosak.

**Eredmény:**
A válasz segített a funkcionális hiányok prioritás szerinti rendezésében.

### 2. Backend javítás
**Prompt:**
Javítsd úgy a backend autentikációt, hogy a CRUD végpontok csak hitelesített felhasználóknak legyenek elérhetők.

**Eredmény:**
Segített az auth guard és a role-alapú jogosultságok kialakításában.

### 3. Dokumentáció
**Prompt:**
Készíts rövid, beadásra alkalmas dokumentációs vázlatot a technológiai stackről és a teljesített követelményekről.

**Eredmény:**
A dokumentációs szerkezet a stack, követelmények és telepítési lépések mentén lett felépítve.

### 4. Kevésbé sikeres prompt
**Prompt:**
Mindent javíts ki.

**Miért volt gyenge:**
Túl tág, nem ad elég kontextust, ezért nehéz belőle célzott fejlesztési lépéseket generálni.

## Melléklet és megjegyzés
A fenti minták demonstrációs jellegűek, és azt mutatják meg, hogyan lehet a fejlesztési folyamatot visszakövethetően dokumentálni.
