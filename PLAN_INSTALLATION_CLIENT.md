# Plan d'Installation et d'Utilisation - Moteur BI Agentique

Ce document détaille, étape par étape, la procédure pour installer et utiliser la solution "Agentic Business Intelligence Engine" sur un poste client.

---

## 1. Prérequis : Installation de Docker

Le moteur BI est entièrement conteneurisé avec Docker. Cela garantit une installation propre et isolée, sans nécessiter Python ou d'autres dépendances sur la machine cliente.

**Action :**
1.  **Créez un compte Docker Hub** si vous n'en avez pas déjà un : [Docker Hub](https://hub.docker.com/).
2.  **Installez Docker Desktop** pour Windows ou macOS, ou Docker Engine pour Linux.
    *   [Docker pour Windows](https://docs.docker.com/desktop/install/windows-install/)
    *   [Docker pour Mac](https://docs.docker.com/desktop/install/mac-install/)
    *   [Docker pour Linux](https://docs.docker.com/engine/install/)

---

## 2. Mise en Place de l'Environnement

Cette section vous guide pour télécharger l'image de l'application et configurer votre environnement local.

### Étape 2.1 : Authentification Docker
Ouvrez un terminal (PowerShell ou CMD sur Windows, Terminal sur macOS/Linux) et connectez-vous à votre compte Docker Hub.

```bash
docker login
```
Saisissez votre nom d'utilisateur et votre mot de passe lorsque vous y êtes invité.

### Étape 2.2 : Téléchargement de l'Image de l'Application
Téléchargez (pull) l'image de l'application depuis le référentiel privé.

```bash
docker pull josueafouda/agentic-b:latest
```

### Étape 2.3 : Création du Répertoire de Travail
Créez un dossier dédié sur votre machine où tous les artefacts générés (rapports, graphiques, etc.) seront stockés.

```bash
mkdir projet-bi-agentique
cd projet-bi-agentique
```

### Étape 2.4 : Création des Dossiers de Données
Dans ce nouveau répertoire, créez les sous-dossiers qui seront synchronisés avec le conteneur.

```bash
mkdir requests sql schema dataviz outputs
```

### Étape 2.5 : Configuration de la Connexion à la Base de Données
Créez un fichier nommé `.env` (sans extension) à la racine de votre répertoire `projet-bi-agentique`. Ce fichier contiendra les informations de connexion sécurisées à votre base de données PostgreSQL.

**Contenu du fichier `.env` :**
```env
DB_HOST=votre_adresse_de_base_de_donnees
DB_PORT=5432
DB_NAME=le_nom_de_votre_db
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
# Optionnel : pour les connexions SSL (ex: require, verify-full)
# DB_SSLMODE=require
```
**Remplacez les valeurs par vos propres informations de connexion.**

---

## 3. Exécution du Workflow BI

Vous êtes maintenant prêt à lancer le moteur BI pour répondre à une question métier.

### Étape 3.1 : Formulation de la Question Métier
Créez un fichier texte simple dans le dossier `requests` contenant la question que vous souhaitez poser.

Par exemple, créez le fichier `requests/top_5_clients.txt` avec le contenu suivant :
```
Quels sont nos cinq meilleurs clients en termes de chiffre d'affaires ?
```

### Étape 3.2 : Lancement de l'Interface (TUI)
Exécutez la commande suivante depuis la racine de votre répertoire `projet-bi-agentique`. Elle lancera l'interface utilisateur textuelle (TUI) de manière interactive.

```bash
docker run --rm -it 
  --env-file ./.env 
  -v "$(pwd)/requests":/app/requests 
  -v "$(pwd)/sql":/app/sql 
  -v "$(pwd)/schema":/app/schema 
  -v "$(pwd)/dataviz":/app/dataviz 
  -v "$(pwd)/outputs":/app/outputs 
  -v gemini-client-config:/home/appuser/.config/@google-gemini-cli 
  josueafouda/agentic-b:latest
```

**Explication de la commande :**
*   `--rm`: Supprime le conteneur après utilisation.
*   `-it`: Lance le conteneur en mode interactif.
*   `--env-file ./.env`: Injecte vos identifiants de base de données.
*   `-v "..."`: Synchronise les dossiers locaux avec ceux du conteneur pour la persistance des données.
*   `gemini-client-config`: Un volume nommé qui sauvegarde votre authentification Google.

### Étape 3.3 : Première Authentification Gemini
La toute première fois que vous lancerez cette commande, l'application vous demandera de vous authentifier avec votre compte Google. Suivez les instructions affichées dans le terminal pour compléter ce processus unique. Votre authentification sera sauvegardée pour les futures exécutions.

### Étape 3.4 : Suivi du Workflow dans la TUI
Une fois authentifié, l'interface vous guidera :
1.  Sélectionnez la base de données et le schéma à analyser.
2.  Indiquez le nom de votre question (`top_5_clients` dans notre exemple).
3.  Validez chaque étape (génération SQL, exécution, visualisation, etc.).

---

## 4. Accès aux Résultats

Une fois le workflow terminé, tous les fichiers générés sont disponibles sur votre machine locale, dans le dossier `outputs/top_5_clients`. Vous y trouverez :
*   Un fichier `.csv` avec les données brutes.
*   Un rapport `.html` interactif (le graphique).
*   Un fichier `.md` avec les analyses et recommandations stratégiques.

Vous pouvez ouvrir ces fichiers directement sur votre machine.

---

## 5. Usage Avancé (Optionnel)

Il est également possible d'exécuter des commandes spécifiques sans passer par l'interface TUI, en les ajoutant à la fin de la commande `docker run`.

**Exemple : Générer uniquement le SQL**
```bash
docker run --rm -it 
  --env-file ./.env 
  -v "$(pwd)/requests":/app/requests 
  -v "$(pwd)/sql":/app/sql 
  -v "$(pwd)/schema":/app/schema 
  -v "$(pwd)/dataviz":/app/dataviz 
  -v "$(pwd)/outputs":/app/outputs 
  -v gemini-client-config:/home/appuser/.config/@google-gemini-cli 
  josueafouda/agentic-b:latest 
  python3 -m scripts.generate_sql --request requests/top_5_clients.txt --database votre_db --schema public
```
