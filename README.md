# Workflow BI Centré-Agent (Agent-centric BI)

![](agent_bi.png)

Ce projet implémente un workflow de Business Intelligence (BI) piloté par l'IA (Gemini CLI), transformant des questions métier en langage naturel en analyses de données exploitables, visualisations interactives et recommandations stratégiques.

---

## 1️⃣ État actuel de la solution

### ✅ Architecture et Orchestration

La solution repose sur une architecture modulaire où chaque étape est déterministe. L'orchestration est assurée par une interface texte (TUI) ou par des appels CLI explicites.

1. **Orchestration via TUI (`scripts/tui2.py`)** :
   * Centralise le workflow complet : de la saisie de la question à la génération d'insights métiers.
   * Gère la régénération du schéma et le nommage des fichiers pour assurer la cohérence.

2. **Workflow Déterministe (Pipeline)** :
   * **Intention** : Les questions sont stockées dans `requests/*.txt`.
   * **SQL** : `generate_sql.py` transforme l'intention en SQL auditable via Gemini.
   * **Analyse** : `run_analysis.py` exécute le SQL et exporte les résultats dans `outputs/` (CSV + Metadata).
   * **Visualisation** : `generate_dataviz.py` et `run_dataviz.py` créent un rapport HTML interactif.
   * **Insights & Actions** : `generate_insights_actions.py` analyse les résultats pour produire des recommandations métiers au format Markdown.

3. **Exécution Contrôlée (Single-File Processing)** :
   * Chaque script traite désormais **un seul fichier spécifique** via des arguments CLI explicites.

4. **Schéma Automatisé** :
   * `schema.py` produit un contexte fiable de la base de données dans `schema/dvdrental_schema.md`.

---

## 2️⃣ Utilisation

### Mode Recommandé (TUI)
L'interface interactive guide l'utilisateur à travers toutes les étapes :
```bash
python3 scripts/tui2.py
```

### Mode Expert (CLI)
Utilisez les scripts comme modules Python :

```bash
# 1. Générer le SQL
python3 -m scripts.generate_sql --request requests/ma_question.txt

# 2. Exécuter l'analyse
python3 -m scripts.run_analysis --sql sql/ma_question.sql

# 3. Générer le code de visualisation
python3 -m scripts.generate_dataviz --request requests/ma_question.txt

# 4. Produire le rapport HTML
python3 -m scripts.run_dataviz --dataviz dataviz/ma_question.py

# 5. Générer les Insights & Actions
python3 -m scripts.generate_insights_actions --request requests/ma_question.txt
```

---

## 3️⃣ Avantages de la solution

* **Analyse Complète** : Va au-delà de la simple extraction de données en proposant des actions concrètes.
* **Contrôle Total** : Une commande = Un fichier traité.
* **Auditabilité** : Chaque étape produit un artefact tangible (SQL, CSV, JSON, HTML, MD).
* **Standardisation** : Utilisation des imports de modules Python (`-m`).

---

## 4️⃣ Roadmap et Améliorations

1. **Multi-SGBDR** : Adaptateurs pour MySQL et SQL Server.
2. **Validation SQL** : Ajout d'une étape de "dry-run" avant exécution.
3. **Sécurité** : Renforcement du contrôle des inputs.

---

## 5️⃣ Schéma de l'Orchestration

```
┌───────────────────┐
│      TUI / CLI    │──▶ Orchestrateur central
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  generate_sql.py  │──▶ Produit sql/<nom>.sql
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  run_analysis.py  │──▶ Produit outputs/<nom>/<nom>.csv
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ generate_dataviz  │──▶ Produit dataviz/<nom>.py
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   run_dataviz.py  │──▶ Produit outputs/<nom>/<nom>.html
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│generate_insights  │──▶ Produit outputs/<nom>/<nom>.md
└───────────────────┘
```
