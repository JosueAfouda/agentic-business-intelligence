-- On définit la période d'analyse basée sur la dernière date de transaction connue
WITH periode_activite AS (
    SELECT MAX(payment_date) AS date_fin FROM payment
),
-- Identification des 5 catégories de films les plus louées historiquement
categories_populaires AS (
    SELECT fc.category_id
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film_category fc ON i.film_id = fc.film_id
    GROUP BY fc.category_id
    ORDER BY COUNT(*) DESC
    LIMIT 5
),
-- Calcul du taux de retard pour chaque client sur l'ensemble de son historique
statistiques_retard_clients AS (
    SELECT 
        r.customer_id,
        AVG(CASE 
            WHEN r.return_date > (r.rental_date + (f.rental_duration || ' days')::interval) THEN 1 
            ELSE 0 
        END) AS taux_retard_individuel
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    WHERE r.return_date IS NOT NULL
    GROUP BY r.customer_id
),
-- Calcul du seuil de retard global (moyenne des taux de retard de tous les clients)
seuil_global AS (
    SELECT AVG(taux_retard_individuel) AS moyenne_globale_retard
    FROM statistiques_retard_clients
)
-- Sélection des 5 clients les plus rentables répondant aux critères
SELECT 
    c.first_name || ' ' || c.last_name AS client,
    SUM(p.amount) AS total_paiements_valides,
    COUNT(r.rental_id) AS nombre_locations_qualifiees
FROM customer c
JOIN payment p ON c.customer_id = p.customer_id
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film_category fc ON i.film_id = fc.film_id
JOIN statistiques_retard_clients src ON c.customer_id = src.customer_id
CROSS JOIN seuil_global sg
WHERE p.payment_date >= (SELECT date_fin FROM periode_activite) - INTERVAL '1 year'
  AND fc.category_id IN (SELECT category_id FROM categories_populaires)
  AND src.taux_retard_individuel < sg.moyenne_globale_retard
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_paiements_valides DESC
LIMIT 5;
