# Schéma de la base olympics_db (Schema: public)

_Note : seules les tables physiques (BASE TABLE) sont prises en compte. Les vues SQL sont volontairement exclues._


## TABLES

- public.athletes
- public.countries
- public.country_stats
- public.summer_games
- public.winter_games

## COLUMNS

- public.athletes | id | integer | YES
- public.athletes | name | character varying | YES
- public.athletes | gender | character varying | YES
- public.athletes | age | integer | YES
- public.athletes | height | integer | YES
- public.athletes | weight | integer | YES
- public.countries | id | integer | YES
- public.countries | country | character varying | YES
- public.countries | region | character varying | YES
- public.country_stats | year | character varying | YES
- public.country_stats | country_id | integer | YES
- public.country_stats | gdp | double precision | YES
- public.country_stats | pop_in_millions | character varying | YES
- public.country_stats | nobel_prize_winners | integer | YES
- public.summer_games | sport | character varying | YES
- public.summer_games | event | character varying | YES
- public.summer_games | year | date | YES
- public.summer_games | athlete_id | integer | YES
- public.summer_games | country_id | integer | YES
- public.summer_games | bronze | double precision | YES
- public.summer_games | silver | double precision | YES
- public.summer_games | gold | double precision | YES
- public.winter_games | sport | character varying | YES
- public.winter_games | event | character varying | YES
- public.winter_games | year | date | YES
- public.winter_games | athlete_id | integer | YES
- public.winter_games | country_id | integer | YES
- public.winter_games | bronze | double precision | YES
- public.winter_games | silver | double precision | YES
- public.winter_games | gold | double precision | YES

## CONSTRAINTS
