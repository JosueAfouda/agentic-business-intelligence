# Agent-centric Business Intelligence Workflow

![](agent_bi.png)

---

## 1️⃣ État actuel de la solution

### ✅ Fonctionnalités déjà implémentées

1. **Workflow Agent-Centric BI**

   * Les questions métiers sont déposées dans `requests/*.txt`.
   * Gemini CLI transforme l’intention métier + schéma en SQL auditable.
   * Le SQL est exécuté directement sur la base de données (PostgreSQL pour l’instant).
   * Les résultats sont exportés dans `outputs/<question_name>/<question_name>.csv` avec `metadata.json` pour traçabilité.

2. **Gestion incremental-safe**

   * `generate_sql.py` ne régénère que les nouvelles questions.
   * `run_analysis.py` n’exécute que les SQL dont les CSV n’existent pas encore.
   * Cela permet un workflow répétable et “batch-friendly” sans écrasement involontaire.

3. **Schéma de base automatisé**

   * `schema.py` produit un fichier `schema/dvdrental_schema.md` avec :

     * tables physiques (`BASE TABLE`)
     * colonnes, types et contraintes (PK/FK)
   * L’agent dispose d’une vue complète et fiable du schéma pour générer des requêtes correctes.

4. **Nettoyage du SQL pour psycopg2**

   * Suppression des backticks Markdown
   * Conversion des commentaires multi-lignes `/* */` en `--`
   * Assure l’exécution directe du SQL via Python.

5. **Logs clairs et auditables**

   * `[OK]` pour les nouvelles exécutions
   * `[SKIP]` pour les fichiers déjà traités
   * Fichiers CSV et `metadata.json` garantissent traçabilité et reproductibilité.

---

## 2️⃣ Avantages actuels de la solution

### 🎯 Pour l’entreprise

* **Autonomie** : plus besoin de Power BI/Tableau pour la production de rapports SQL simples à complexes.
* **Coût réduit** : utilise PostgreSQL (ou autres SGBDR gratuits) + Agents IA gratuits.
* **Versioning et auditabilité** : chaque question et résultat est versionné et traceable.
* **Rapid iteration** : nouvelle question → génération automatique SQL → CSV exploitable.
* **Transparence** : SQL lisible et auditable, pas de “boîte noire” comme certains outils SaaS.

### 🚀 Pour la technique / workflow

* Pipeline **100% text-based / agent-driven**.
* Compatible avec **plusieurs questions en batch**.
* Base solide pour ajout de couches supplémentaires : insights narratifs, alerting, scoring.

---

## 3️⃣ Limites actuelles / points d’amélioration

1. **Multi-SGBDR**

   * PostgreSQL est déjà implémenté.
   * Pour MySQL / SQL Server :

     * Adapter `db_utils.py` pour chaque driver (`mysql-connector-python`, `pyodbc`).
     * Adapter `schema.py` pour la syntaxe `information_schema` spécifique.
     * Adapter le template Gemini pour tenir compte des particularités syntaxiques (ex : `LIMIT` vs `TOP`, concaténation de chaînes).

2. **Gestion avancée des questions**

   * Pour l’instant, pas de “update automatique” si la question change.
   * Possible amélioration : hash du contenu `.txt` et comparaison avec `metadata.json`.

3. **Analyse plus riche / narrative**

   * Génération automatique d’insights ou de recommandations métiers à partir des CSV.
   * Exemple : “Le top 10 clients représente 45% du chiffre d’affaires”.

4. **Sécurité / access control**

   * Pour usage entreprise, penser à :

     * lecture seule sur DB
     * journalisation des exécutions
     * contrôle des inputs de Gemini pour éviter injection de code SQL malicieux.

5. **Standardisation et réutilisabilité**

   * Créer un template SQL “clean & safe” pour tout SGBDR.
   * Option : un seul projet avec un **adapter layer** pour PostgreSQL/MySQL/SQL Server.

6. **Scalabilité**

   * Pour de grandes bases ou plusieurs questions simultanées, prévoir :

     * parallélisation (multi-thread ou job queue)
     * cache / stockage des résultats intermédiaires

---

## 4️⃣ Opportunités stratégiques

* **PME et startups** : ton outil offre un accès “professionnel” à la BI **sans licence payante**.
* **Workflow Agent-Centric BI** : permet aux équipes non techniques de poser des questions métier directement à leurs données brutes.
* **Extensible** : futur ajout de GPT / Gemini pour insights narratifs → décision rapide → alerting → tableau de bord minimaliste si besoin.
* **Support multi-SGBDR** : pourrait devenir un **standard open-source pour BI autonome** sur bases locales (PostgreSQL, MySQL, SQL Server).

---

## 5️⃣ Roadmap V2 / prochaines améliorations

1. **Multi-SGBDR** : adapter utils et scripts pour MySQL et SQL Server
2. **Insights narratifs** : générer un résumé texte à partir du CSV pour les décisions rapides
3. **Mode batch multi-questions** avec logs consolidés
4. **Interface minimaliste (optionnelle)** pour poser les questions via CLI ou web léger
5. **Pipeline complet “Post-BI”** : intention → SQL → exécution → CSV → insight → alerting

---

💡 **Conclusion**

Tu as aujourd’hui un **outil BI agent-driven fonctionnel**, incrémental, traçable et gratuit pour petites et moyennes entreprises.
Il permet de **remplacer Power BI/Tableau pour l’extraction et l’analyse directe des données**, tout en ouvrant la voie vers des **insights narratifs et décisionnels avancés**.

---

## 1️⃣ Schéma ASCII (README friendly)

```
┌───────────────────┐
│   Question métier │
│   (NL text)       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  generate_sql.py  │
│ - Lit question    │
│ - Lit schema      │
│ - Appelle Gemini  │
│ - Génère SQL      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   SQL généré      │
│ (auditable, clean)│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  run_analysis.py  │
│ - Exécute SQL     │
│ - Génère CSV      │
│ - Génère metadata │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Résultat exploitable│
│ CSV + metadata     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Insights / Actions│
│ - Analyse métrique│
│ - Dashboard léger │
│ - Alerting option │
└───────────────────┘
```

---

## 2️⃣ Schéma conceptuel pour image (Diagramme)

**Flux logique de la solution :**

1. **Question métier (NL)**

   * déposée dans `requests/*.txt`
   * “Quels sont les clients qui ont effectué les paiements totaux les plus élevés ?”

2. **Génération SQL (Agent)**

   * `generate_sql.py` + Gemini CLI
   * Schéma DB comme contexte (`schema/dvdrental_schema.md`)
   * Nettoyage SQL (`clean_sql`)
   * Résultat : `sql/<question>.sql`

3. **Exécution SQL**

   * `run_analysis.py`
   * Exécute uniquement les SQL non traités
   * Génère `outputs/<question>/<question>.csv` + `metadata.json`

4. **Résultat exploitable**

   * CSV prêt à analyser ou visualiser
   * Métadonnées pour audit / traçabilité

5. **Optionnel : Insights narratifs / alerting**

   * Génération automatique de commentaires / alertes métiers
   * Possibilité de mini-dashboard léger ou export vers outil BI secondaire si besoin

---

### 🟢 Key Points

* Workflow **100% text-based** et **agent-driven**
* **Incremental-safe** : anciens fichiers SQL ou CSV non écrasés
* **Extensible** : multi-SGBDR (PostgreSQL / MySQL / SQL Server)
* **Open-source-friendly** : idéal pour PME/startups avec budget limité

---

