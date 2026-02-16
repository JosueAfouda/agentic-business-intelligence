# Workflow BI Centré-Agent (Agent-centric BI)

![](agent_bi.png)

Ce projet implémente un workflow de Business Intelligence (BI) piloté par l'IA (Gemini CLI), transformant des questions métier en langage naturel en analyses de données exploitables et visualisations interactives.

---

## 1️⃣ État actuel de la solution

### ✅ Architecture et Orchestration

La solution repose sur une architecture modulaire où chaque étape est déterministe. L'orchestration est assurée par une interface texte (TUI) ou par des appels CLI explicites.

1. **Orchestration via TUI (`scripts/tui.py`)** :
   * Centralise le workflow : de la saisie de la question à la génération du rapport HTML final.
   * Gère la régénération du schéma et le nommage des fichiers pour assurer la cohérence.

2. **Workflow Déterministe (Pipeline)** :
   * **Intention** : Les questions sont stockées dans `requests/*.txt`.
   * **SQL** : `generate_sql.py` transforme l'intention en SQL auditable via Gemini.
   * **Analyse** : `run_analysis.py` exécute le SQL et exporte les résultats dans `outputs/` (CSV + Metadata).
   * **Visualisation** : `generate_dataviz.py` crée un script Plotly, et `run_dataviz.py` génère le rapport HTML final.

3. **Exécution Contrôlée (Single-File Processing)** :
   * Chaque script traite désormais **un seul fichier spécifique** via des arguments CLI explicites (`--request`, `--sql`, etc.).
   * Fin de l'itération automatique sur les dossiers pour une sécurité et une traçabilité accrues.

4. **Schéma Automatisé** :
   * `schema.py` produit un contexte fiable de la base de données dans `schema/dvdrental_schema.md`.

---

## 2️⃣ Utilisation

### Mode Recommandé (TUI)
L'interface interactive guide l'utilisateur à travers toutes les étapes :
```bash
python3 scripts/tui.py
```

### Mode Expert (CLI)
Pour un contrôle granulaire ou une intégration CI/CD, utilisez les scripts comme modules Python :

```bash
# 1. Générer le SQL
python3 -m scripts.generate_sql --request requests/ma_question.txt

# 2. Exécuter l'analyse
python3 -m scripts.run_analysis --sql sql/ma_question.sql

# 3. Générer le code de visualisation
python3 -m scripts.generate_dataviz --request requests/ma_question.txt

# 4. Produire le rapport HTML
python3 -m scripts.run_dataviz --dataviz dataviz/ma_question.py
```

---

## 3️⃣ Avantages de la solution

* **Contrôle Total** : Une commande = Un fichier traité. Pas d'exécution involontaire sur d'anciennes requêtes.
* **Auditabilité** : Chaque étape produit un artefact tangible (SQL, CSV, JSON, HTML) consultable.
* **Modularité** : Facile d'étendre à d'autres SGBDR (MySQL, etc.) en modifiant uniquement la couche `utils/`.
* **Standardisation** : Utilisation des imports de modules Python (`-m`) pour une résolution propre des dépendances internes.

---

## 4️⃣ Roadmap et Améliorations

1. **Multi-SGBDR** : Adaptateurs pour MySQL et SQL Server.
2. **Insights Narratifs** : Génération d'un résumé textuel des découvertes à partir du CSV.
3. **Validation SQL** : Ajout d'une étape de "dry-run" ou de linting SQL avant exécution.
4. **Sécurité** : Renforcement du contrôle des inputs pour prévenir les injections SQL.

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
└───────────────────┘
```
