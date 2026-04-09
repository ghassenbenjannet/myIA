# Plan d’implémentation MVP — MyIA / RoleConfig AI

## 1) Architecture cible (MVP)

- **Frontend** : interface web (sélection profil, prompt, réponse, feedback, dashboard minimal).
- **Backend API** : gestion profils, exécutions, feedback, tests.
- **Prompt Builder** : construction du prompt système à partir de la configuration.
- **LLM Gateway** : abstraction fournisseur LLM.
- **Storage** : base relationnelle pour profils/versions/exécutions/feedback/tests.
- **Evaluator** : scoring conformité + format (règles simples au MVP).

## 2) Incréments fonctionnels

### Sprint A — Fondations

- Modèle de données des profils + versions.
- CRUD profil (brouillon, actif, désactivé).
- 3 profils templates : PO, Comptable, Chercheur.
- Prompt Builder v1.
- Génération de réponse simple.

### Sprint B — Gouvernance minimale

- Journalisation exécution complète.
- Affichage règles actives.
- Feedback utile/pas utile + motif.
- Cas de test basiques + exécution batch.

### Sprint C — Pilotage MVP

- Score conformité/format v1.
- Seuil de publication bloquant.
- Dashboard minimal (usage, conformité, feedback, escalade).

## 3) Schéma de données minimal

- `profil_configuration`
- `version_profil`
- `execution`
- `cas_de_test`
- `feedback`

## 4) Définition de prêt (DoR)

Une US est prête si :
- rôle utilisateur clair,
- critères d’acceptation testables,
- dépendances identifiées,
- maquettes ou structure de sortie définie.

## 5) Définition de terminé (DoD)

Une US est terminée si :
- critères d’acceptation passants,
- logs présents,
- tests automatisés unitaires/intégration passants,
- documentation mise à jour,
- démonstration métier validée.

## 6) KPI de pilotage MVP

- Temps médian de réponse,
- Taux de conformité,
- Taux de feedback positif,
- Taux de réponses avec incertitude/escalade,
- Nombre de profils actifs.

## 7) Risques techniques MVP

- Variabilité des sorties LLM,
- Coût et latence API,
- Faible différenciation inter-profils,
- Scoring conformité trop binaire.

## 8) Actions de mitigation

- Prompts structurés + contraintes format,
- Caching partiel et timeout,
- Cas de test discriminants par profil,
- Rubrique "incertitudes et limites" obligatoire sur profils à prudence élevée.
