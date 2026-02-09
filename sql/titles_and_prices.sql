SELECT
    title AS titre_film,
    rental_rate AS tarif_location
FROM
    film
WHERE
    rental_rate IN (0.99, 2.99);
