# Cahier des charges — Projet **RoleConfig AI**

## 1. Présentation du projet

### 1.1 Nom du projet

**RoleConfig AI** — Plateforme d’assistant LLM configurable par métier et par contexte d’usage.

### 1.2 Contexte

Les assistants IA généralistes répondent de manière trop uniforme à des besoins différents selon les métiers. Un Product Owner, un comptable, un chercheur ou un agent support n’attendent ni le même niveau de rigueur, ni les mêmes formats de sortie, ni les mêmes garde-fous.

L’objectif du projet est de concevoir un socle unique d’assistant LLM capable d’adapter dynamiquement son comportement grâce à une configuration explicite, sans reconstruire un assistant spécifique pour chaque métier.

### 1.3 Vision produit

Permettre à une organisation de déployer rapidement des assistants IA fiables, gouvernables et extensibles, en configurant leur rôle, leurs sources, leurs règles de prudence, leur format de sortie et leurs comportements attendus.

### 1.4 Problème à résoudre

Les usages LLM en entreprise rencontrent souvent les limites suivantes :

- réponses trop génériques ;
- manque de contrôle du comportement ;
- difficulté à industrialiser plusieurs cas d’usage ;
- absence de garde-fous métier ;
- manque de traçabilité des configurations ;
- difficulté à mesurer la qualité et la conformité des réponses.

### 1.5 Objectif principal

Créer une plateforme permettant de générer des réponses LLM adaptées à un métier ou à un contexte d’usage à partir d’une configuration déclarative, testable et versionnable.

### 1.6 Objectifs secondaires

- Réduire le temps de création de nouveaux assistants métier.
- Standardiser la gouvernance des assistants IA.
- Améliorer la qualité et la pertinence des réponses.
- Permettre la comparaison entre plusieurs profils de configuration.
- Faciliter l’évaluation et l’amélioration continue.

## 2. Périmètre du projet

### 2.1 Périmètre inclus

Le projet couvre :

- la création et la gestion de profils de configuration ;
- la génération de réponses LLM selon un profil ;
- la sélection de sources autorisées ;
- l’application de garde-fous ;
- le choix d’un format de sortie ;
- la journalisation des exécutions ;
- l’évaluation de conformité des réponses ;
- la comparaison de profils sur un même prompt ;
- la gestion des versions de configuration ;
- une interface utilisateur de démonstration / exploitation.

### 2.2 Hors périmètre initial

- entraînement d’un modèle propriétaire ;
- fine-tuning d’un LLM ;
- gestion d’identités avancée entreprise (SSO complexe) ;
- déploiement multi-tenant à grande échelle ;
- facturation / monétisation ;
- connecteurs métier complexes en temps réel (ERP/CRM) en phase 1.

## 3. Parties prenantes

### 3.1 Sponsor

Direction Produit / Innovation / Ops IA.

### 3.2 Parties prenantes clés

- Product Owner
- Engineering Lead
- Développeurs front/back
- Expert IA / LLM Engineer
- UX/UI Designer
- Référents métiers
- QA / Test manager
- Utilisateurs pilotes

### 3.3 Utilisateurs cibles

- Product Owner
- Comptable / expert métier
- Chercheur / analyste
- Support client
- Admin / configurateur
- Manager / sponsor souhaitant suivre les métriques

## 4. Personas

### Persona 1 — Pauline, Product Owner

Souhaite obtenir des analyses structurées, user stories, critères d’acceptation, risques, edge cases.

### Persona 2 — Karim, Comptable

Souhaite des réponses prudentes, rigoureuses, fondées sur des sources autorisées, avec refus ou escalade en cas d’incertitude.

### Persona 3 — Sofia, Chercheuse

Souhaite des réponses nuancées, comparatives, sourcées et explicitant limites et hypothèses.

### Persona 4 — Louis, Admin IA

Souhaite créer, modifier, tester et versionner des profils de configuration sans modifier le code cœur.

### Persona 5 — Emma, Manager

Souhaite suivre les indicateurs d’usage, de conformité et de qualité des assistants.

## 5. Proposition de valeur

### 5.1 Valeur utilisateur

- Réponses mieux adaptées au contexte métier.
- Réduction des reformulations manuelles.
- Amélioration de la confiance dans les réponses.
- Standardisation des usages IA.

### 5.2 Valeur business

- Réutilisation d’un même socle pour plusieurs métiers.
- Réduction du coût de déploiement de nouveaux assistants.
- Gouvernance et contrôle renforcés.
- Meilleure adoption grâce à des expériences personnalisées.

## 6. Hypothèses produit

- Les utilisateurs acceptent qu’un même moteur LLM soit configuré plutôt que remplacé selon le métier.
- Une configuration explicite permet d’augmenter la qualité perçue.
- La capacité à tester et comparer les profils accélère l’amélioration continue.
- Les garde-fous visibles renforcent la confiance des utilisateurs.

## 7. Parcours utilisateurs principaux

### 7.1 Parcours “Utiliser un profil existant”

1. L’utilisateur ouvre l’application.
2. Il sélectionne un profil métier.
3. Il saisit son besoin.
4. Le moteur applique la configuration.
5. Le LLM génère une réponse.
6. La réponse est affichée dans le format attendu.
7. L’utilisateur peut donner un feedback ou comparer avec un autre profil.

### 7.2 Parcours “Créer un nouveau profil”

1. L’admin accède à l’espace de configuration.
2. Il crée un nouveau profil.
3. Il définit le rôle, les objectifs, les garde-fous, les sources et le format.
4. Il teste le profil sur des cas de test.
5. Il publie une version.

### 7.3 Parcours “Évaluer la qualité”

1. Le manager consulte le tableau de bord.
2. Il filtre par profil, période, score, type d’usage.
3. Il identifie les non-conformités et cas à améliorer.

## 8. Fonctionnalités détaillées

### Epic 1 — Gestion des profils de configuration

**Objectif :** Permettre la création, modification, duplication, activation, désactivation et versionning des profils de configuration.

**Fonctionnalités :**

- Créer un profil
- Modifier un profil
- Dupliquer un profil
- Supprimer / archiver un profil
- Activer / désactiver un profil
- Gérer les versions d’un profil
- Visualiser l’historique des modifications

### Epic 2 — Modélisation de la configuration

**Objectif :** Définir de manière structurée les paramètres de comportement du LLM.

**Paramètres attendus :**

- nom du profil ;
- description ;
- rôle ;
- objectif principal ;
- ton ;
- niveau de détail ;
- niveau de prudence / risque ;
- politique d’hallucination ;
- politique de clarification ;
- sources autorisées ;
- contraintes métier ;
- garde-fous ;
- formats de sortie autorisés ;
- skills activés ;
- critères d’évaluation ;
- règles d’escalade ;
- métadonnées de version.

### Epic 3 — Génération de réponse

**Objectif :** Permettre à un utilisateur d’obtenir une réponse LLM conforme au profil sélectionné.

**Fonctionnalités :**

- Saisie libre d’une demande
- Sélection d’un profil
- Construction dynamique du prompt système
- Appel LLM
- Affichage de la réponse
- Affichage des règles appliquées

### Epic 4 — Gestion des sources et du contexte

**Objectif :** Restreindre et piloter les sources utilisées par le modèle.

**Fonctionnalités :**

- Sélection des sources autorisées par profil
- Ajout de documents contextuels
- Utilisation ou non d’un mode RAG
- Visualisation des sources utilisées

### Epic 5 — Formats de sortie

**Objectif :** Produire des réponses sous une forme directement exploitable.

**Formats visés :** analyse structurée, user story, critères d’acceptation, email, plan d’action, synthèse, note métier, comparaison, tableau, plan de recherche.

### Epic 6 — Garde-fous et conformité

**Objectif :** Garantir un comportement encadré et prédictible du système.

**Fonctionnalités :**

- règles de non hallucination ;
- règles de clarification ;
- règles de refus ;
- règles d’escalade ;
- mention explicite des limites.

### Epic 7 — Comparaison de profils

**Objectif :** Comparer les effets de différentes configurations sur une même demande.

### Epic 8 — Évaluation et tests

**Objectif :** Mesurer la conformité et la qualité des réponses.

### Epic 9 — Feedback utilisateur

**Objectif :** Permettre la remontée et l’exploitation du ressenti utilisateur.

### Epic 10 — Journalisation et traçabilité

**Objectif :** Permettre l’audit des exécutions et la compréhension du comportement du système.

### Epic 11 — Dashboard et pilotage

**Objectif :** Donner de la visibilité sur l’usage, la qualité et la conformité.

### Epic 12 — Administration et droits

**Objectif :** Séparer les usages consultation, configuration et pilotage.

## 9. Exigences non fonctionnelles

- **Performance** : temps de réponse cible < 8 secondes sur cas simple ; état de chargement visible.
- **Disponibilité** : cible MVP 95 %.
- **Sécurité** : séparation des rôles, protection des logs, masquage des données sensibles, traçabilité des modifications.
- **Maintenabilité** : configuration séparée du code, architecture modulaire, documentation technique minimale.
- **Scalabilité** : ajout de nouveaux profils sans refonte.
- **Observabilité** : logs exploitables, suivi erreurs techniques/fonctionnelles.
- **UX** : interface simple, profil actif lisible, feedback clair en cas d’incertitude/refus/erreur.

## 10. Règles de gestion

- Un profil doit avoir un rôle, un objectif et au moins un garde-fou.
- Un profil brouillon ne peut pas être utilisé en production.
- Une publication crée automatiquement une nouvelle version.
- Un profil non conforme au seuil minimal de tests ne peut pas être publié.
- Un profil désactivé ne peut pas être sélectionné par un utilisateur standard.
- Une exécution doit toujours journaliser le profil et la version utilisés.
- Si l’input est ambigu et que la politique l’impose, le système doit demander une clarification avant de répondre.
- Si la politique de risque est stricte, le système doit préférer l’incertitude ou l’escalade à l’invention.

## 11. Données métier / objets principaux

### Entité `ProfilConfiguration`

- id, nom, description, rôle, objectif, ton, niveau_detail, niveau_prudence,
- formats_autorises, sources_autorisees, garde_fous, règles_escalade,
- skills_actifs, statut, version_courante, auteur, date_creation, date_modification.

### Entité `VersionProfil`

- id, profil_id, numéro_version, contenu_configuration, date_publication, auteur, statut.

### Entité `Execution`

- id, utilisateur, profil_id, version_id, prompt, réponse, sources_utilisées,
- score_conformité, score_format, statut, date_execution.

### Entité `CasDeTest`

- id, profil_id (optionnel), intitulé, prompt, attentes, critères, score_obtenu, statut.

### Entité `Feedback`

- id, execution_id, utile_oui_non, motif, commentaire, date.

## 12. MVP recommandé

**Contenu MVP :**

- sélection d’un profil ;
- 3 profils prêts à l’emploi : PO, comptable, chercheur ;
- saisie d’une demande ;
- réponse générée selon configuration ;
- affichage du format de sortie ;
- affichage des règles actives ;
- stockage des exécutions ;
- feedback simple ;
- campagne basique de tests ;
- tableau de bord minimal.

## 13. Backlog priorisé

- **P1** : gestion profils, config, sélection profil, génération, formats, garde-fous de base, logs.
- **P2** : versionning, cas de test, score conformité, dashboard, feedback, comparaison profils.
- **P3** : import documentaire, RAG, évaluation avancée, workflow validation, droits avancés.

## 14. Découpage par releases

- **Release 1 — Fondations** : modèle de configuration, 3 profils initiaux, génération simple, réponse + métadonnées, logs.
- **Release 2 — Gouvernance** : versionning, tests, publication, score conformité, feedback.
- **Release 3 — Industrialisation** : comparaison de profils, dashboard avancé, import documentaire, RAG sélectif, droits avancés.

## 15. Critères de succès produit

- 3 profils configurés fonctionnels au MVP ;
- au moins 80 % des cas de test MVP conformes ;
- temps de création d’un nouveau profil < 30 min ;
- démonstration claire de différences de comportement entre profils ;
- logs et version disponibles pour 100 % des exécutions ;
- feedback utilisateur exploitable.

## 16. Risques produit

- configuration trop complexe ;
- résultats LLM insuffisamment différenciés ;
- difficulté à mesurer la qualité ;
- mauvaise compréhension des garde-fous ;
- surcharge cognitive côté admin.

**Mesures de réduction :** limiter le MVP, fournir des templates, imposer des champs structurants, créer des tests représentatifs, afficher les règles actives de manière pédagogique.

## 17. Dépendances

- accès à un fournisseur LLM ;
- choix d’une stack front/back ;
- stockage des configurations et logs ;
- disponibilité de référents métiers pour les profils initiaux ;
- disponibilité QA pour les cas de test.

## 18. Contraintes

- l’assistant ne doit pas être présenté comme infaillible ;
- toute réponse doit être rattachée à un profil et une version ;
- les règles métier doivent être configurables sans toucher au cœur du code ;
- le projet doit rester démontrable en POC.

## 19. Stories complémentaires par profil métier

### Profil PO

- transformer un besoin flou en user story ;
- identifier critères d’acceptation ;
- détecter zones d’ambiguïté ;
- proposer edge cases ;
- suggérer risques et dépendances.

### Profil Comptable

- répondre avec prudence ;
- distinguer faits, hypothèses, exceptions ;
- indiquer manque de données ;
- escalader si nécessaire.

### Profil Chercheur

- produire une synthèse nuancée ;
- expliciter hypothèses ;
- comparer des approches ;
- citer ou signaler les limites des sources.

## 20. Annexes — exemples de formats de sortie

### Format User Story

- Contexte
- Besoin
- User Story
- Critères d’acceptation
- Risques
- Questions ouvertes

### Format Analyse structurée

- Résumé
- Hypothèses
- Analyse
- Risques
- Recommandations

### Format Synthèse comparative

- Sujet
- Option A
- Option B
- Comparaison
- Limites
- Conclusion

## 21. Conclusion

RoleConfig AI est une plateforme IA orientée produit, gouvernance et industrialisation. Sa valeur réside dans la capacité à configurer, contrôler, tester, comparer et améliorer le comportement du LLM selon les besoins métier.
