WITH last_activity AS (
    SELECT MAX(rental_date) AS max_date
    FROM rental
),
analysis_period AS (
    SELECT 
        max_date - INTERVAL '1 year' AS start_date
    FROM last_activity
),
top_categories AS (
    -- Identification des 5 catégories les plus populaires par volume de location sur la période
    SELECT fc.category_id
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film_category fc ON i.film_id = fc.film_id
    JOIN analysis_period p ON r.rental_date >= p.start_date
    GROUP BY fc.category_id
    ORDER BY COUNT(*) DESC
    LIMIT 5
),
customer_delays AS (
    -- Calcul du taux de retard par client sur la dernière année (toutes catégories)
    -- Un retard est défini par une date de retour > date de location + durée de location
    SELECT 
        r.customer_id,
        AVG(CASE 
            WHEN r.return_date > r.rental_date + (f.rental_duration * INTERVAL '1 day') THEN 1.0 
            ELSE 0.0 
        END) AS delay_rate
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    JOIN analysis_period p ON r.rental_date >= p.start_date
    WHERE r.return_date IS NOT NULL
    GROUP BY r.customer_id
),
global_delay_benchmark AS (
    -- Moyenne globale des taux de retard des clients
    SELECT AVG(delay_rate) AS avg_delay_threshold
    FROM customer_delays
),
customer_revenue AS (
    -- Revenus générés par client uniquement sur les films des catégories top 5
    SELECT 
        p.customer_id,
        SUM(p.amount) AS total_revenue
    FROM payment p
    JOIN rental r ON p.rental_id = r.rental_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film_category fc ON i.film_id = fc.film_id
    JOIN analysis_period ap ON r.rental_date >= ap.start_date
    WHERE fc.category_id IN (SELECT category_id FROM top_categories)
    GROUP BY p.customer_id
)
SELECT 
    c.first_name || ' ' || c.last_name AS client_nom,
    ROUND(cr.total_revenue, 2) AS revenu_categories_top,
    ROUND((cd.delay_rate * 100)::numeric, 2) AS taux_retard_pourcentage
FROM customer c
JOIN customer_revenue cr ON c.customer_id = cr.customer_id
JOIN customer_delays cd ON c.customer_id = cd.customer_id
CROSS JOIN global_delay_benchmark gdb
WHERE cd.delay_rate < gdb.avg_delay_threshold
ORDER BY cr.total_revenue DESC
LIMIT 5;
