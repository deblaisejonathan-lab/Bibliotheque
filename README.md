# Système de Gestion de Bibliothèque (MVC & SQLite)

Application en ligne de commande développée en **Python** selon une architecture **MVC (Modèle - Vue - Contrôleur)** avec persistance des données dans **SQLite** (`data/bibliotheque.db`) et importation automatique de livres via l'API publique **Open Library**.

## Fonctionnalités

- **Gestion du catalogue** : consulter la liste des livres, ajouter un livre manuellement ou importer des livres depuis l'API Open Library.
- **Gestion des adhérents** : inscrire de nouveaux membres (`id_membre`, nom, prénom, email, statut) et afficher la liste des inscrits.
- **Guichet d'emprunt et de retour** : enregistrer un emprunt avec calcul automatique de la date de retour prévue (14 jours par défaut), gérer le retour d'un livre avec détection des jours de retard et consulter les emprunts en cours.

## Architecture du projet

```text
bIBLIOTHEQUE/
├── APPs/
│   ├── __init__.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── controllers.py   # Orchestration des actions et du menu
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py        # Entités (Livre, Membre, Emprunt), SQLite & API Open Library
│   └── views/
│       ├── __init__.py
│       └── views.py         # Affichage console et saisies utilisateur
├── data/
│   └── bibliotheque.db      # Base de données SQLite générée automatiquement
├── main.py                  # Point d'entrée de l'application
└── README.md
