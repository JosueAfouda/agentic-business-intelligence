WITH active_customers AS (
    -- Sélection des clients actifs uniquement
    SELECT customer_id, store_id, first_name, last_name, email
    FROM customer
    WHERE activebool = true
),
customer_payments AS (
    -- Chiffre d'affaires cumulé par client actif
    SELECT
        p.customer_id,
        SUM(p.amount) as total_revenue
    FROM payment p
    JOIN active_customers ac ON p.customer_id = ac.customer_id
    GROUP BY p.customer_id
),
customer_rentals_stats AS (
    -- Statistiques de location par client : fréquence et performance de retour (durée de rétention)
    SELECT
        r.customer_id,
        COUNT(r.rental_id) as rental_count,
        AVG(EXTRACT(EPOCH FROM (r.return_date - r.rental_date))) as avg_return_duration_seconds
    FROM rental r
    JOIN active_customers ac ON r.customer_id = ac.customer_id
    WHERE r.return_date IS NOT NULL
    GROUP BY r.customer_id
),
global_thresholds AS (
    -- Calcul des seuils sur la population active : Top 10% CA et Médiane fréquence
    SELECT
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY cp.total_revenue) as revenue_p90,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY crs.rental_count) as rental_frequency_median
    FROM customer_payments cp
    JOIN customer_rentals_stats crs ON cp.customer_id = crs.customer_id
),
store_performance_benchmark AS (
    -- Performance moyenne de retour par magasin (référence basée sur les clients actifs)
    SELECT
        ac.store_id,
        AVG(crs.avg_return_duration_seconds) as store_avg_return_seconds
    FROM customer_rentals_stats crs
    JOIN active_customers ac ON crs.customer_id = ac.customer_id
    GROUP BY ac.store_id
),
film_rental_volumes AS (
    -- Volume de location par film (demande globale)
    SELECT
        i.film_id,
        COUNT(r.rental_id) as rental_volume
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    GROUP BY i.film_id
),
high_demand_film_threshold AS (
    -- Seuil pour le top 25% des films les plus demandés
    SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rental_volume) as volume_p75
    FROM film_rental_volumes
),
high_demand_films AS (
    -- Liste des films très demandés
    SELECT f.film_id
    FROM film_rental_volumes f
    CROSS JOIN high_demand_film_threshold t
    WHERE f.rental_volume >= t.volume_p75
),
customer_film_preferences AS (
    -- Analyse des préférences : proportion de films très demandés loués par le client
    SELECT
        r.customer_id,
        COUNT(r.rental_id) as total_rentals_checked,
        COUNT(CASE WHEN i.film_id IN (SELECT film_id FROM high_demand_films) THEN 1 END) as high_demand_count
    FROM rental r
    JOIN active_customers ac ON r.customer_id = ac.customer_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    GROUP BY r.customer_id
)
SELECT
    ac.customer_id,
    ac.first_name,
    ac.last_name,
    ac.email,
    ac.store_id,
    cp.total_revenue,
    crs.rental_count,
    ROUND((cfp.high_demand_count::numeric / NULLIF(cfp.total_rentals_checked, 0)) * 100, 2) as pct_high_demand_films,
    ROUND((crs.avg_return_duration_seconds / 86400)::numeric, 2) as avg_return_days,
    ROUND((spb.store_avg_return_seconds / 86400)::numeric, 2) as benchmark_store_days
FROM active_customers ac
JOIN customer_payments cp ON ac.customer_id = cp.customer_id
JOIN customer_rentals_stats crs ON ac.customer_id = crs.customer_id
JOIN customer_film_preferences cfp ON ac.customer_id = cfp.customer_id
JOIN store_performance_benchmark spb ON ac.store_id = spb.store_id
CROSS JOIN global_thresholds gt
WHERE cp.total_revenue >= gt.revenue_p90 -- Top 10% chiffre d'affaires
  AND crs.rental_count > gt.rental_frequency_median -- Fréquence > Médiane
  AND (cfp.high_demand_count::numeric / NULLIF(cfp.total_rentals_checked, 0)) > 0.5 -- Majoritairement (>50%) des films très demandés
  AND crs.avg_return_duration_seconds < spb.store_avg_return_seconds -- Performance meilleure (durée plus courte) que la moyenne magasin
ORDER BY cp.total_revenue DESC;
