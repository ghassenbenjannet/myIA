# Shadow PO AI Frontend

## Stack

- React
- Vite
- TypeScript
- React Router
- TanStack Query
- Zustand
- Tailwind CSS
- shadcn/ui-style components

## Commandes

1. Installer Node.js 20+
2. Depuis `frontend/` :

```bash
npm install
npm run dev
```

Le serveur Vite est configure pour proxyfier les appels API vers `http://localhost:8000`.

## Docker Compose

Depuis la racine du repo :

```bash
docker compose up --build
```

URLs de dev :

- frontend React/Vite : `http://localhost:5173`
- backend FastAPI : `http://localhost:8000`
- front statique FastAPI temporaire : `http://localhost:8000/`

Dans Docker, Vite :

- ecoute sur `0.0.0.0`
- active le polling pour le hot reload
- proxy les appels API vers le service backend `app`

## Parcours principaux

- `/` : Dashboard
- `/topics` : liste des topics
- `/topics/:topicId` : workspace d'un topic
- `/artifacts/:runId` : detail d'un artefact
- `/reads` : source summary / jira read / confluence read
- `/lookup` : run lookup et continuation
- `/workspace` : nouveau travail
