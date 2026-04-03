# Nyelvcsere Frontend

Vue 3 + Vite alapú kliens a Nyelvcsere Közösség projekthez.

## Előfeltételek

- Node.js 20.19+ (vagy 22.12+)
- Futó backend API (alapértelmezés: `http://127.0.0.1:8000`)

## Környezeti változók

Hozz létre `frontend/.env` fájlt a `frontend/.env.example` alapján:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Fejlesztés

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Teszt

```bash
npm run test
```

## Fontos route-ok

- `/` kezdőoldal
- `/mentors` mentorlista (vendégként is elérhető)
- `/sessions` foglalkozások kezelése
- `/profile` profil és haladás
- `/dashboard` mentor dashboard
