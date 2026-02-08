-- Analyse des clients à haute valeur et performance sur les 24 derniers mois
-- Critères : Top 10% CA, Régularité > Médiane, >50% films forte rotation, performance retour > magasin

WITH bounds AS (
    -- Définition de la fenêtre temporelle : 24 mois précédant la dernière location enregistrée
    SELECT 
        MAX(rental_date) as last_activity_date,
        MAX(rental_date) - INTERVAL '24 months' as start_date
    FROM rental
),
film_rotation AS (
    -- Identification des films à forte rotation (Top 25% des volumes de location sur la période)
    SELECT 
        i.film_id,
        PERCENT_RANK() OVER (ORDER BY COUNT(r.rental_id) ASC) as rotation_percentile
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    CROSS JOIN bounds b
    WHERE r.rental_date >= b.start_date
    GROUP BY i.film_id
),
customer_activity AS (
    -- Calcul des indicateurs par client sur la période
    SELECT 
        c.customer_id,
        c.store_id,
        c.first_name,
        c.last_name,
        SUM(p.amount) as total_revenue,
        COUNT(r.rental_id) as rental_count,
        -- Ratio de films à forte rotation (Top 25% = percentile > 0.75)
        COUNT(CASE WHEN fr.rotation_percentile >= 0.75 THEN 1 END)::numeric / NULLIF(COUNT(*), 0) as high_rotation_ratio,
        -- Performance de retour : Retard pondéré par la durée du film (0 si en avance/à l'heure)
        -- Formule : (Temps effectif - Temps alloué) / Temps alloué
        AVG(
            CASE 
                WHEN r.return_date IS NULL THEN NULL 
                ELSE 
                    GREATEST(0, EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) - (f.rental_duration * 86400)) 
                    / NULLIF(f.rental_duration * 86400, 0)
            END
        ) as weighted_delay_score
    FROM customer c
    JOIN rental r ON c.customer_id = r.customer_id
    JOIN payment p ON r.rental_id = p.rental_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    JOIN film_rotation fr ON f.film_id = fr.film_id
    CROSS JOIN bounds b
    WHERE r.rental_date >= b.start_date
    GROUP BY c.customer_id, c.store_id, c.first_name, c.last_name
),
store_benchmarks AS (
    -- Performance moyenne de retour par magasin
    SELECT 
        store_id,
        AVG(weighted_delay_score) as store_avg_delay_score
    FROM customer_activity
    GROUP BY store_id
),
global_thresholds AS (
    -- Seuils globaux : Top 10% CA et Médiane de régularité
    SELECT 
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_revenue) as revenue_threshold_top10,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY rental_count) as median_regularity
    FROM customer_activity
)
SELECT 
    ca.first_name as prenom_client,
    ca.last_name as nom_client,
    ROUND(ca.total_revenue, 2) as ca_cumule,
    ca.rental_count as nombre_locations,
    ROUND((ca.high_rotation_ratio * 100), 1) as pct_films_forte_rotation,
    ROUND(ca.weighted_delay_score::numeric, 4) as score_retard_client,
    ROUND(sb.store_avg_delay_score::numeric, 4) as score_retard_magasin
FROM customer_activity ca
JOIN store_benchmarks sb ON ca.store_id = sb.store_id
CROSS JOIN global_thresholds gt
WHERE ca.total_revenue >= gt.revenue_threshold_top10
  AND ca.rental_count > gt.median_regularity
  AND ca.high_rotation_ratio > 0.5
  AND ca.weighted_delay_score < sb.store_avg_delay_score
ORDER BY ca.total_revenue DESC;
