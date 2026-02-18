-- Analyse du salaire moyen et de l'effectif par ethnie
SELECT 
    ethnicity AS "Ethnie",
    ROUND(AVG(salary), 2) AS "Salaire Moyen",
    COUNT(employee_id) AS "Nombre d'Employés"
FROM 
    hr_analytics.dim_employee
GROUP BY 
    ethnicity
ORDER BY 
    "Salaire Moyen" DESC;
