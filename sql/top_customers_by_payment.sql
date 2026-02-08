-- Identification des clients ayant généré le plus de chiffre d'affaires
SELECT 
    c.first_name AS prenom,
    c.last_name AS nom,
    SUM(p.amount) AS total_paye
FROM 
    customer c
JOIN 
    payment p ON c.customer_id = p.customer_id
GROUP BY 
    c.customer_id, 
    c.first_name, 
    c.last_name
ORDER BY 
    total_paye DESC;
