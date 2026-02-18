-- Analyse de la répartition des effectifs par tranche d'âge et par genre
SELECT
    CASE
        WHEN age < 20 THEN '<20'
        WHEN age BETWEEN 20 AND 29 THEN '20-29'
        WHEN age BETWEEN 30 AND 39 THEN '30-39'
        WHEN age BETWEEN 40 AND 49 THEN '40-49'
        ELSE '50+'
    END AS groupe_age,
    gender AS genre,
    COUNT(*) AS nombre_total_employes
FROM
    hr_analytics.dim_employee
GROUP BY
    groupe_age,
    genre
ORDER BY
    groupe_age,
    genre;
