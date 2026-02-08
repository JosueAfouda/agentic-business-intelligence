-- Liste détaillée des paiements clients avec les intervenants associés
SELECT 
    c.first_name || ' ' || c.last_name AS nom_client,
    s.first_name || ' ' || s.last_name AS membre_personnel,
    p.amount AS montant,
    p.payment_date AS date_paiement
FROM 
    payment p
JOIN 
    customer c ON p.customer_id = c.customer_id
JOIN 
    staff s ON p.staff_id = s.staff_id
ORDER BY 
    p.payment_date;
