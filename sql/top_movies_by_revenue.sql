-- Identification des dix films générant le plus de revenus
SELECT
    f.title AS titre_du_film,
    SUM(p.amount) AS revenu_total
FROM
    film f
JOIN
    inventory i ON f.film_id = i.film_id
JOIN
    rental r ON i.inventory_id = r.inventory_id
JOIN
    payment p ON r.rental_id = p.rental_id
GROUP BY
    f.film_id,
    f.title
ORDER BY
    revenu_total DESC
LIMIT 10;
