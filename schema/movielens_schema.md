# Schéma de la base movielens

_Note : seules les tables physiques (BASE TABLE) sont prises en compte. Les vues SQL sont volontairement exclues._


## TABLES

- employees
- genome_scores
- genome_tags
- links
- movies
- ratings
- shifts
- tags

## COLUMNS

- employees | emp_id | integer | NO
- employees | name | character varying | NO
- genome_scores | movieid | integer | NO
- genome_scores | tagid | integer | NO
- genome_scores | relevance | double precision | YES
- genome_tags | tagid | integer | NO
- genome_tags | tag | text | YES
- links | movieid | integer | NO
- links | imdbid | integer | YES
- links | tmdbid | double precision | YES
- movies | movieid | integer | NO
- movies | title | text | YES
- movies | genres | text | YES
- ratings | userid | integer | NO
- ratings | movieid | integer | NO
- ratings | rating | double precision | YES
- ratings | timestamp | text | YES
- shifts | shift_id | integer | NO
- shifts | shift_time | character varying | NO
- tags | userid | integer | NO
- tags | movieid | integer | NO
- tags | tag | text | NO
- tags | timestamp | text | NO

## CONSTRAINTS

- employees | CHECK | None | None | None
- employees | CHECK | None | None | None
- employees | PRIMARY KEY | emp_id | employees | emp_id
- genome_scores | CHECK | None | None | None
- genome_scores | CHECK | None | None | None
- genome_scores | FOREIGN KEY | tagid | genome_tags | tagid
- genome_scores | FOREIGN KEY | movieid | movies | movieid
- genome_scores | PRIMARY KEY | movieid | genome_scores | tagid
- genome_scores | PRIMARY KEY | movieid | genome_scores | movieid
- genome_scores | PRIMARY KEY | tagid | genome_scores | tagid
- genome_scores | PRIMARY KEY | tagid | genome_scores | movieid
- genome_tags | CHECK | None | None | None
- genome_tags | PRIMARY KEY | tagid | genome_tags | tagid
- links | CHECK | None | None | None
- links | FOREIGN KEY | movieid | movies | movieid
- links | PRIMARY KEY | movieid | links | movieid
- movies | CHECK | None | None | None
- movies | PRIMARY KEY | movieid | movies | movieid
- ratings | CHECK | None | None | None
- ratings | CHECK | None | None | None
- ratings | FOREIGN KEY | movieid | movies | movieid
- ratings | PRIMARY KEY | movieid | ratings | movieid
- ratings | PRIMARY KEY | userid | ratings | userid
- ratings | PRIMARY KEY | userid | ratings | movieid
- ratings | PRIMARY KEY | movieid | ratings | userid
- shifts | CHECK | None | None | None
- shifts | CHECK | None | None | None
- shifts | PRIMARY KEY | shift_id | shifts | shift_id
- tags | CHECK | None | None | None
- tags | CHECK | None | None | None
- tags | CHECK | None | None | None
- tags | CHECK | None | None | None
- tags | FOREIGN KEY | movieid | movies | movieid
- tags | PRIMARY KEY | userid | tags | timestamp
- tags | PRIMARY KEY | userid | tags | tag
- tags | PRIMARY KEY | userid | tags | movieid
- tags | PRIMARY KEY | userid | tags | userid
- tags | PRIMARY KEY | movieid | tags | tag
- tags | PRIMARY KEY | timestamp | tags | movieid
- tags | PRIMARY KEY | timestamp | tags | tag
- tags | PRIMARY KEY | timestamp | tags | timestamp
- tags | PRIMARY KEY | tag | tags | timestamp
- tags | PRIMARY KEY | tag | tags | tag
- tags | PRIMARY KEY | tag | tags | movieid
- tags | PRIMARY KEY | tag | tags | userid
- tags | PRIMARY KEY | movieid | tags | timestamp
- tags | PRIMARY KEY | timestamp | tags | userid
- tags | PRIMARY KEY | movieid | tags | movieid
- tags | PRIMARY KEY | movieid | tags | userid