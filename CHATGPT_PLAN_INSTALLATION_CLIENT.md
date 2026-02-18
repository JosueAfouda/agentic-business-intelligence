# INSTALLATION_CLIENT.md

## Installation et utilisation de la solution *Agentic Business Intelligence* via Docker

---

## 1. Objectif du document

Ce document décrit **pas à pas** :

* l’installation de la solution *Agentic Business Intelligence* sur le PC d’un client
* la configuration de l’accès à une base PostgreSQL distante
* l’exécution du workflow complet :

  * question métier
  * génération SQL
  * extraction des données
  * visualisation
  * insights & recommandations

L’objectif est que **la seule chose requise côté client soit Docker**, sans installation de Python ni de dépendances.

---

## 2. Prérequis côté client

### 2.1 Système

* PC **Windows 10 ou 11**
* Accès Internet
* Accès réseau à la base PostgreSQL (VPN si nécessaire)

### 2.2 Logiciels requis

* **Docker Desktop**
  👉 [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

> ⚠️ Docker Desktop doit être démarré avant toute manipulation.

---

## 3. Accès à l’image Docker

Le client reçoit :

* un accès au repository Docker privé
* le nom de l’image Docker :

```text
josueafouda/agentic-b:latest
```

### 3.1 Connexion à Docker Hub

Dans un terminal (PowerShell ou CMD) :

```bash
docker login
```

Entrer :

* Docker Hub username
* Docker Hub password

---

### 3.2 Récupération de l’image

```bash
docker pull josueafouda/agentic-b:latest
```

---

## 4. Préparation de l’environnement local

### 4.1 Créer un dossier de travail

Exemple :

```text
C:\agentic-bi\
```

Dans ce dossier, créer la structure suivante :

```text
agentic-bi/
├─ requests/
├─ sql/
├─ schema/
├─ dataviz/
├─ outputs/
├─ .env
├─ docker-compose.yml
```

---

### 4.2 Créer le fichier `.env`

Dans `agentic-bi/.env`, renseigner les accès PostgreSQL fournis par l’entreprise :

```env
DB_HOST=remote-postgres.company.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=********
DB_SSLMODE=require
```

> ℹ️ Si la base n’impose pas SSL, `DB_SSLMODE` peut être omis.

---

### 4.3 Créer le fichier `docker-compose.yml`

```yaml
services:
  agentic-bi:
    image: josueafouda/agentic-b:latest
    env_file:
      - .env
    stdin_open: true
    tty: true
    volumes:
      - ./requests:/app/requests
      - ./sql:/app/sql
      - ./schema:/app/schema
      - ./dataviz:/app/dataviz
      - ./outputs:/app/outputs
      - ./.gemini_state:/home/appuser/.config
```

---

## 5. Premier lancement (authentification Gemini)

Depuis le dossier `agentic-bi/` :

```bash
docker compose run --rm agentic-bi
```

### 5.1 Authentification Gemini (première fois uniquement)

* Une invite apparaît dans le terminal
* Un lien est fourni pour se connecter avec un **compte Google (Gmail)**
* Ouvrir le lien dans le navigateur
* Se connecter
* Valider l’autorisation

👉 L’authentification est **mémorisée** localement dans `.gemini_state`.

---

## 6. Utilisation via le TUI (mode recommandé)

Le **TUI (Text User Interface)** guide l’utilisateur étape par étape.

### 6.1 Lancement du TUI

```bash
docker compose run --rm agentic-bi
```

### 6.2 Workflow TUI

1. Sélection de la base de données PostgreSQL
2. Sélection du schéma
3. Saisie de la question métier
4. Nom de la question
5. Génération automatique :

   * schéma
   * SQL
   * données
   * graphique
   * insights & recommandations

👉 Les résultats sont disponibles dans le dossier `outputs/`.

---

## 7. Utilisation via le CLI (mode avancé)

Le CLI permet d’exécuter chaque étape séparément.

---

### 7.1 Exemple de question métier

Créer un fichier :

```text
requests/top_customers_by_revenue.txt
```

Contenu :

```text
Quels sont les clients ayant généré le plus de chiffre d’affaires ?
```

---

### 7.2 Génération du schéma

```bash
docker compose run --rm agentic-bi \
  python -m scripts.schema --database dvdrental --schema public
```

---

### 7.3 Génération du SQL

```bash
docker compose run --rm agentic-bi \
  python -m scripts.generate_sql \
  --request requests/top_customers_by_revenue.txt \
  --database dvdrental \
  --schema public
```

---

### 7.4 Exécution de la requête SQL

```bash
docker compose run --rm agentic-bi \
  python -m scripts.run_analysis \
  --sql sql/top_customers_by_revenue.sql \
  --database dvdrental \
  --schema public
```

---

### 7.5 Génération de la visualisation

```bash
docker compose run --rm agentic-bi \
  python -m scripts.generate_dataviz \
  --request requests/top_customers_by_revenue.txt
```

---

### 7.6 Génération du graphique HTML

```bash
docker compose run --rm agentic-bi \
  python -m scripts.run_dataviz \
  --dataviz dataviz/top_customers_by_revenue.py
```

---

### 7.7 Génération des Insights & Actions

```bash
docker compose run --rm agentic-bi \
  python -m scripts.generate_insights_actions \
  --request requests/top_customers_by_revenue.txt
```

---

## 8. Résultats générés

Dans :

```text
outputs/top_customers_by_revenue/
```

On trouve :

* `top_customers_by_revenue.csv` → données
* `top_customers_by_revenue.html` → graphique interactif
* `top_customers_by_revenue.md` → insights & recommandations
* `metadata.json` → métadonnées techniques

👉 Le fichier HTML peut être ouvert directement dans un navigateur.

---

## 9. Bonnes pratiques pour le client

* Toujours passer par le TUI pour un usage métier
* Utiliser le CLI pour des cas avancés
* Conserver les dossiers `outputs/`, `sql/`, `schema/` comme artefacts d’audit
* Ne jamais partager l’image Docker sans autorisation

---

## 10. Support

En cas de problème :

* vérifier l’accès réseau à PostgreSQL
* vérifier les variables du `.env`
* vérifier que Docker Desktop est actif
* contacter le fournisseur de la solution

---

## Fin du document

