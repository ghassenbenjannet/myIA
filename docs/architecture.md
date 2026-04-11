# Architecture — Shadow PO AI

## 1. Objectif

Shadow PO AI est une IA métier personnelle conçue comme un **système de travail pour Product Owner**.

L’objectif n’est pas de construire un chatbot générique, ni un modèle fondation, mais un système modulaire capable d’assister le PO dans un environnement legacy complexe, en s’appuyant sur les outils centraux de travail :

- Jira
- Confluence
- Azure DevOps

Le système doit aider à transformer des demandes floues, des notes brutes, des incidents et des besoins incomplets en livrables exploitables, tout en restant :

- fiable
- explicable
- maintenable
- économe en tokens
- évolutif

---

## 2. Principes d’architecture

## 2.1. Système de travail, pas simple chatbot

Le système est conçu comme un moteur de workflows métier.  
Il doit guider, structurer, qualifier, reformuler et préparer des livrables, pas simplement répondre à des questions.

## 2.2. Orchestration centrale forte

Le système repose sur un **orchestrateur central** qui reçoit la demande, choisit le bon workflow, sélectionne le contexte utile, appelle les bons modules et applique les garde-fous.

Le point de départ n’est pas une constellation d’agents autonomes.

## 2.3. Modules spécialisés à périmètre étroit

Chaque composant métier doit avoir un rôle limité, des entrées claires, des sorties typées et un comportement testable.

## 2.4. Human in the loop

Au démarrage, l’IA prépare.  
L’humain valide.  
L’écriture automatique dans Jira, Confluence ou Azure DevOps n’est pas prioritaire au MVP.

## 2.5. Frugalité token

Le système doit :

- classifier avant de générer
- charger uniquement le contexte nécessaire
- éviter les prompts géants
- éviter les appels LLM inutiles
- privilégier des workflows courts et explicites

## 2.6. Explicabilité

Le système doit distinguer clairement :

- ce qui est certain
- ce qui est déduit
- ce qui est supposé
- ce qui reste à confirmer

C’est une exigence forte dans un contexte legacy riche en ambiguïtés métier et techniques.

---

## 3. Finalité métier du système

Le système doit à terme être capable de :

- analyser un sujet flou
- distinguer bug / évolution / analyse / recette / pilotage PO
- structurer des notes brutes
- produire des tickets propres
- préparer des fiches Azure DevOps
- aider à produire ou mettre à jour Confluence
- détecter risques, dépendances, impacts et ambiguïtés
- assister la structuration du backlog et des travaux PO

L’arbitrage métier final reste du ressort du Product Owner.

---

## 4. Vision fonctionnelle

Le système est conçu autour de 5 fonctions majeures :

### 4.1. Qualification
Identifier la nature réelle de la demande :

- analyse
- bug
- évolution
- recette
- documentation
- pilotage PO
- simple question

### 4.2. Structuration
Transformer un input brut ou flou en contenu exploitable.

### 4.3. Production
Générer un draft structuré selon un format métier attendu.

### 4.4. Vérification
Contrôler la cohérence, les manques, les ambiguïtés, les hypothèses et la qualité de sortie.

### 4.5. Intégration outils
Lire et exploiter le contexte provenant de Jira, Confluence et Azure DevOps, puis plus tard proposer ou exécuter des mises à jour contrôlées.

---

## 5. Architecture logique

## 5.1. Vue d’ensemble

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