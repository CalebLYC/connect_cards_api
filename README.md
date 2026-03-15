# ConnectCards Backend

Backend API pour de Connect Cards pour l'authentification par carte avec **FastAPI**, **SQLAlchemy** et **PostgreSQL**.

---

## Sommaire

- [ConnectCards Backend](#connectcards-backend)
  - [Sommaire](#sommaire)
  - [Prérequis](#prérequis)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Migrations / Initialisation de la base](#migrations--initialisation-de-la-base)
    - [Tableau comparatif](#tableau-comparatif)
  - [Lancement du serveur](#lancement-du-serveur)
  - [Structure du projet](#structure-du-projet)
  - [Commandes utiles](#commandes-utiles)
  - [Tips \& erreurs fréquentes](#tips--erreurs-fréquentes)
  - [Auteur](#auteur)

---

## Prérequis

- Python 3.10+
- PostgreSQL
- [Poetry](https://python-poetry.org/) ou pip
<!--- Alembic (si vous utilisez la méthode Alembic)-->

---

## Installation

1. Cloner le dépôt et se placer dans le projet :

   ```bash
   git clone https://github.com/CalebLYC/connect_cards_api
   cd connect_card_backend
   ```

2. Créer et activer un environnement virtuel :

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## Configuration

1. Créer le fichier `.env` à partir de `.env.exemple` et adapter les valeurs :

   ```bash
   cp .env.exemple .env
   ```

     - Synchrone (driver par défaut) :

       ```bash
       postgresql+psycopg2://user:password@localhost:5432/connect_cards
       ```

     - Asynchrone :

       ```bash
       postgresql+asyncpg://user:password@localhost:5432/connect_cards
       ```

2. **Configurer Alembic** (si utilisé) :

   - Initialiser alembic (si le dossier /migrations n'existe pas ou soit le supprimer pour recommencer à zéro)

    ```bash
     alembic init migrations 
     ```

   - Modifier `alembic.ini` :

   ```bash
   sqlalchemy.url = postgresql+psycopg2://user:password@localhost:5432/connect_cards
   ```

   - Cette URL doit correspondre à votre base et inclure le driver correct.

   > Alembic utilise **psycopg2** par défaut, ce qui garantit la compatibilité avec PostgreSQL.

   - Modifier /migrations/env.py
      - Importe les models et la base

          ```python
          from app.models.permission import Permission
          from app.models.role import Role
          from app.models.user import User
          from app.models.access_token import AccessToken
          # Import another models
          # ...
          from app.models.base import Base
          ```

      - Utiliser la base sqlachemy
      Changer la ligne:
  
       ```python
      Base = None
      ```
  
      en:

      ```python
      Base = Base.metadata
      ```

3. Créer la base de données si elle n’existe pas :

```sql
CREATE DATABASE connect_cards;
```

---

## Migrations / Initialisation de la base

Vous pouvez **choisir entre Alembic ou scripts SQL manuels**.

### Tableau comparatif

| Étape                         | Alembic                                                   | Scripts SQL manuels                                       |
| ----------------------------- | --------------------------------------------------------- | --------------------------------------------------------- |
| Générer la structure initiale | `alembic revision --autogenerate -m "Initial tables"`     | Non nécessaire (tables dans `scripts/sql/schema.sql`)     |
| Appliquer les migrations      | `alembic upgrade head`                                    | `psql -U user -d connect_cards -f scripts/sql/schema.sql` |
| Seeds / données initiales     | Ajouter une migration spécifique ou `scripts/seeds/*.sql` | `psql -U user -d connect_cards -f scripts/seeds/*.sql`    |
| Notes                         | Alembic utilise `psycopg2` par défaut, fiable             | Permet de gérer la DB sans Alembic                        |

> Vous pouvez **utiliser l’une ou l’autre méthode**, pas besoin de combiner.

---

## Lancement du serveur

```bash
uvicorn app.main:app --reload
```

Documentation interactive :

- Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)
  
---

## Structure du projet

```text
app/
│
├── core/                # Configurations & sécurité (config.py, jwt.py, security.py, etc.)
├── controllers/         # Endpoints FastAPI
├── db/                  # Connexion DB & Repositories
│   └── repositories/    # Classes repository par entité
├── models/              # Modèles SQLAlchemy
├── providers/           # Providers & middlewares (auth_middleware, role_middleware, etc.)
├── services/            # Logique métier
├── utils/               # Fonctions utilitaires
│
scripts/
├── seeds/               # Scripts d’insertion de données initiales
└── sql/                 # Scripts SQL manuels
│
migrations/              # Versions Alembic
```

---

## Commandes utiles

- Installer les dépendances :

  ```bash
  pip install -r requirements.txt
  ```

- Créer une migration (Alembic) :

  ```bash
  alembic revision --autogenerate -m "Message"
  ```

- Appliquer les migrations (Alembic) :

  ```bash
  alembic upgrade head
  ```

- Exécuter les scripts SQL manuellement :

  ```bash
  psql -U user -d connect_cards -f scripts/sql/*.sql
  ```

- Lancer le serveur :

  ```bash
  uvicorn app.main:app --reload
  ```

---

## Tips & erreurs fréquentes

- **Driver PostgreSQL** : assurez-vous que `psycopg2` (synchrone) ou `asyncpg` (asynchrone) correspond à votre configuration.
- **Fuseau horaire dans DateTime** : SQLAlchemy convertit automatiquement `datetime` naïf en UTC, mais certaines opérations peuvent lever des erreurs si un timezone est présent.
- **Alembic + asyncpg** : si vous utilisez asyncpg, Alembic fonctionne toujours avec psycopg2 pour les migrations, même si votre app est asynchrone.
- **Ordre d’exécution des scripts SQL** : exécuter d’abord `schema.sql`, puis les fichiers `seeds`.
- **Permissions PostgreSQL** : assurez-vous que l’utilisateur a les droits CREATE et INSERT sur la base.
- **Backups** : toujours tester sur une DB de dev avant d’appliquer les migrations en prod.

---

## Auteur

ConnectInc / CalebLyc

---
