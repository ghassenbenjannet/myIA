# Shadow PO AI

## Vision

Shadow PO AI est une IA métier personnelle conçue comme un **système de travail** pour Product Owner, et non comme un simple chatbot.

Son rôle est d’aider à transformer des demandes floues, des notes brutes, des incidents, des besoins métier incomplets et des sujets legacy complexes en livrables exploitables :

* analyses structurées
* tickets propres
* fiches Azure DevOps pour les développeurs
* pages Confluence
* plans de recette
* listes de risques, dépendances, ambiguïtés et questions ouvertes

Le projet vise une architecture **modulaire, frugale en tokens, explicable, maintenable et évolutive**.

---

## Objectif produit

Construire progressivement une IA de type **Shadow PO** capable de :

* analyser un sujet flou
* distinguer bug / évolution / analyse / recette / pilotage PO
* structurer des notes brutes
* produire des drafts de tickets et de documentation
* détecter les points à clarifier
* signaler risques, impacts et dépendances
* s’appuyer sur Jira, Confluence et Azure DevOps comme outils centraux

L’IA n’a pas vocation à remplacer le PO sur l’arbitrage métier. Elle prépare, structure, challenge et assiste. Le PO valide les décisions finales.

---

## Principes directeurs

### 1. Value first

Chaque brique développée doit apporter une valeur visible rapidement.

### 2. Architecture avant sophistication

Pas de constellation d’agents autonomes au départ. Le système commence avec un orchestrateur central fort et des modules spécialisés à périmètre étroit.

### 3. Human in the loop

Au début, l’IA prépare. L’humain valide. L’écriture automatique dans les outils vient plus tard.

### 4. Strong contracts

Chaque module doit avoir des entrées/sorties typées, un périmètre clair et un comportement testable.

### 5. Token efficiency

Le système doit charger le minimum de contexte nécessaire, router avant de générer, et éviter les prompts géants.

### 6. Explainability

Le système doit distinguer clairement :

* ce qui est certain
* ce qui est déduit
* ce qui est supposé
* ce qui doit être confirmé

---

## Ce que le système doit faire

### Cible idéale

* analyser un sujet métier flou
* classifier la demande
* proposer une reformulation claire
* détecter les ambiguïtés
* lister les questions ouvertes
* proposer des tickets ou fiches de travail
* produire des drafts de documentation
* aider à structurer le backlog
* s’appuyer sur les données Jira / Confluence / Azure DevOps
* fonctionner par workflows modulaires

### Cible MVP

* prendre un texte libre en entrée
* qualifier la demande
* produire une analyse structurée
* produire un draft ticket ou un draft documentation
* appliquer une couche de vérification qualité
* fonctionner sans écriture automatique dans les outils

### Hors périmètre initial

* autonomie complète sur les outils
* multi-agent complexe
* mémoire vectorielle globale branchée partout
* écriture automatique directe en production
* assistant universel couvrant tous les usages

---

## Architecture MVP

Le MVP démarre avec une architecture simple, robuste et maintenable.

### Composants principaux

#### 1. Orchestrateur central

Responsable de :

* recevoir la demande
* classifier l’intention
* choisir le workflow
* sélectionner le contexte minimal
* appeler le bon module spécialisé
* appliquer la logique anti-token
* déclencher la vérification qualité

#### 2. Intent classifier

Détermine :

* type de demande
* niveau de complexité
* besoin de contexte externe
* format de sortie attendu

#### 3. Modules spécialisés

Le MVP démarre avec trois modules :

* **Analysis Module** : transforme un sujet flou en analyse structurée
* **Ticket Module** : génère un draft ticket propre
* **Documentation Module** : génère un draft de documentation ou de note structurée

#### 4. Quality Gate

Vérifie :

* présence des champs attendus
* distinction entre faits et hypothèses
* ambiguïtés restantes
* points à confirmer
* conformité au format attendu

#### 5. Tool Connectors

Connecteurs vers :

* Jira
* Confluence
* Azure DevOps

Au départ, usage principalement en lecture.

#### 6. Storage

Stockage structuré pour :

* configuration
* templates
* historique des runs
* sorties produites
* feedback utilisateur
* journalisation

---

## Workflow MVP principal

### Input libre → qualification → analyse → draft exploitable

Exemple d’entrée :

> Le métier dit que la remise ne se calcule plus pareil pour les produits désactivés, mais on ne sait pas si ça concerne aussi les imports batch.

Sortie attendue :

* type de demande
* reformulation
* hypothèses
* zones floues
* risques
* dépendances
* questions ouvertes
* proposition de livrable
* draft ticket ou draft analyse

---

## Architecture logique simplifiée

```text
[Client / UI / Chat / CLI]
        |
        v
[Orchestrateur central]
        |
        +--> [Intent Classifier]
        |
        +--> [Context Selector]
        |
        +--> [Workflow Engine]
                 |
                 +--> [Analysis Module]
                 +--> [Ticket Module]
                 +--> [Documentation Module]
                 +--> [Quality Gate]
        |
        +--> [Tool Connectors]
                 +--> Jira
                 +--> Confluence
                 +--> Azure DevOps
        |
        +--> [Storage]
                 +--> PostgreSQL
```

---

## Stack technique recommandée

### Langage

* Python

### Backend

* FastAPI

### Validation / schémas

* Pydantic

### Persistance

* PostgreSQL
* SQLAlchemy

### LLM / orchestration

* orchestration maison légère au départ
* possibilité d’introduire LangGraph ou PydanticAI plus tard si nécessaire

### Connecteurs

* Jira REST API
* Confluence REST API
* Azure DevOps REST API

### Observabilité

* logging structuré
* historique des runs
* versioning des prompts

---

## Structure cible du repository

```text
shadow-po-ai/
├── README.md
├── app/
│   ├── api/
│   ├── core/
│   ├── orchestrator/
│   ├── modules/
│   │   ├── analysis/
│   │   ├── ticket/
│   │   └── documentation/
│   ├── connectors/
│   │   ├── jira/
│   │   ├── confluence/
│   │   └── azure_devops/
│   ├── quality/
│   ├── prompts/
│   ├── schemas/
│   ├── services/
│   └── storage/
├── tests/
├── docs/
│   ├── architecture.md
│   └── mvp-scope.md
└── pyproject.toml
```

---

## MVP v1 — périmètre de développement

### Inclus

* backend local exécutable
* endpoint principal de traitement
* orchestrateur central
* classifieur d’intention
* module d’analyse
* module ticket
* module documentation
* quality gate
* stockage minimal
* prompts versionnés
* connecteurs mockés ou lecture seule selon disponibilité

### Exclu dans un premier temps

* interface utilisateur avancée
* écriture automatique dans Jira / Confluence / ADO
* autonomie complète
* mémoire vectorielle transverse
* raisonnement multi-agent complexe

---

## Critères de succès du MVP

Le MVP est réussi si :

* il produit des drafts utiles au quotidien
* il fait gagner du temps réel au PO
* il structure correctement un sujet flou
* il réduit le travail de reformulation manuelle
* il met en évidence les points à clarifier
* il reste simple à maintenir
* il consomme peu de tokens

Le MVP est raté si :

* il produit du texte générique
* il hallucine trop
* il dépend d’énormes prompts
* il est difficile à tester
* il devient une usine à gaz avant d’être utile

---

## Feuille de route initiale

### Sprint 1

* cadrage technique détaillé
* structure du projet
* schémas de données
* orchestrateur minimal
* endpoint API principal
* workflow de qualification

### Sprint 2

* module d’analyse
* module ticket
* quality gate
* persistance minimale

### Sprint 3

* module documentation
* versioning des prompts
* logs et historique des runs
* premiers tests métier

### Sprint 4

* connecteurs Jira / Confluence / Azure DevOps en lecture
* récupération ciblée de contexte
* enrichissement du routing

### Sprint 5

* écriture contrôlée avec validation humaine
* amélioration qualité
* scoring de confiance
* optimisation token

---

## Mode de fonctionnement attendu

Le système doit fonctionner comme un assistant métier discipliné :

1. qualifier avant d’agir
2. charger le minimum de contexte utile
3. produire un draft structuré
4. signaler les incertitudes
5. soumettre à validation humaine
6. écrire dans les outils uniquement lorsque le niveau de confiance et les garde-fous sont suffisants

---

## Prochaine étape

La prochaine étape du projet est la rédaction de la **spec technique MVP v1**, qui définira précisément :

* les composants
* leurs responsabilités
* les schémas d’entrée/sortie
* les règles de routage
* le premier backlog de développement

Ce document servira ensuite de base à la génération du squelette de code.
---

## Lancement Docker en developpement

Le projet peut etre lance en developpement via Docker Compose avec :

```bash
docker compose up --build
```

URLs disponibles :

- backend FastAPI : `http://localhost:8000`
- frontend React/Vite : `http://localhost:5173`
- front statique FastAPI temporaire : `http://localhost:8000/`

Le backend reste servi par le service `app`. Le nouveau frontend React vit dans `frontend/`, tourne dans son propre conteneur Vite, et proxy les appels API vers le backend sans changer les contrats existants.
