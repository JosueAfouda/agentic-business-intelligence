-- Définition de la période d'analyse : la dernière année d'activité enregistrée dans la base
WITH periode_activite AS (
    SELECT MAX(payment_date) - INTERVAL '1 year' AS date_limite
    FROM payment
),
-- Identification des catégories les plus louées (celles dont le volume de location est supérieur à la moyenne)
categories_populaires AS (
    SELECT fc.category_id
    FROM film_category fc
    JOIN inventory i ON fc.film_id = i.film_id
    JOIN rental r ON i.inventory_id = r.inventory_id
    GROUP BY fc.category_id
    HAVING COUNT(r.rental_id) > (
        SELECT AVG(nb_locations)
        FROM (
            SELECT COUNT(r2.rental_id) AS nb_locations
            FROM film_category fc2
            JOIN inventory i2 ON fc2.film_id = i2.film_id
            JOIN rental r2 ON i2.inventory_id = r2.inventory_id
            GROUP BY fc2.category_id
        ) sub
    )
),
-- Calcul du taux de retard individuel par client sur l'ensemble de son historique
comportement_retard AS (
    SELECT 
        r.customer_id,
        COUNT(CASE WHEN r.return_date > r.rental_date + (f.rental_duration * INTERVAL '1 day') THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(r.rental_id), 0) AS taux_retard_client
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    WHERE r.return_date IS NOT NULL
    GROUP BY r.customer_id
),
-- Calcul du taux de retard moyen global pour servir de seuil de comparaison
moyenne_globale AS (
    SELECT AVG(taux_retard_client) AS moyenne_seuil
    FROM comportement_retard
)
-- Sélection des 5 clients les moins rentables répondant aux critères de fiabilité (retard inférieur à la moyenne)
SELECT 
    c.first_name || ' ' || c.last_name AS "Client",
    SUM(p.amount) AS "Chiffre d'Affaires (Top Catégories)",
    ROUND(cr.taux_retard_client, 4) AS "Taux de Retard Moyen"
FROM customer c
JOIN payment p ON c.customer_id = p.customer_id
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN comportement_retard cr ON c.customer_id = cr.customer_id
WHERE p.payment_date >= (SELECT date_limite FROM periode_activite)
AND fc.category_id IN (SELECT category_id FROM categories_populaires)
AND cr.taux_retard_client < (SELECT moyenne_seuil FROM moyenne_globale)
GROUP BY c.customer_id, c.first_name, c.last_name, cr.taux_retard_client
ORDER BY "Chiffre d'Affaires (Top Catégories)" ASC
LIMIT 5;
