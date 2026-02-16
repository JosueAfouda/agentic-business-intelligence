-- Sélection des 10 premiers clients ayant effectué les paiements totaux les plus élevés
SELECT
    c.customer_id AS id_client,
    c.first_name AS prenom,
    c.last_name AS nom,
    SUM(p.amount) AS montant_total_paye
FROM
    customer c
JOIN
    payment p ON c.customer_id = p.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name
ORDER BY
    montant_total_paye DESC
LIMIT 10;
