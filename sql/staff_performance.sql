-- Performance des membres du staff au fil du temps (ventes et transactions)
SELECT 
    s.first_name || ' ' || s.last_name AS membre_staff,
    DATE_TRUNC('month', p.payment_date)::DATE AS mois_paiement,
    SUM(p.amount) AS montant_total_ventes,
    COUNT(p.payment_id) AS nombre_transactions
FROM 
    staff s
JOIN 
    payment p ON s.staff_id = p.staff_id
GROUP BY 
    membre_staff, 
    mois_paiement
ORDER BY 
    mois_paiement DESC, 
    montant_total_ventes DESC;
