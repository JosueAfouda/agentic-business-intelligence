# Schéma de la base mlops_realestate

_Note : seules les tables physiques (BASE TABLE) sont prises en compte. Les vues SQL sont volontairement exclues._


## TABLES

- ingestion_log
- raw_real_estate

## COLUMNS

- ingestion_log | id | integer | NO
- ingestion_log | file_name | text | NO
- ingestion_log | file_type | text | YES
- ingestion_log | ingestion_date | timestamp without time zone | YES
- raw_real_estate | id_annonce | bigint | NO
- raw_real_estate | property_type | text | YES
- raw_real_estate | approximate_latitude | double precision | YES
- raw_real_estate | approximate_longitude | double precision | YES
- raw_real_estate | city | text | YES
- raw_real_estate | postal_code | integer | YES
- raw_real_estate | size | double precision | YES
- raw_real_estate | floor | double precision | YES
- raw_real_estate | land_size | double precision | YES
- raw_real_estate | energy_performance_value | double precision | YES
- raw_real_estate | energy_performance_category | text | YES
- raw_real_estate | ghg_value | double precision | YES
- raw_real_estate | ghg_category | text | YES
- raw_real_estate | exposition | text | YES
- raw_real_estate | nb_rooms | double precision | YES
- raw_real_estate | nb_bedrooms | double precision | YES
- raw_real_estate | nb_bathrooms | double precision | YES
- raw_real_estate | nb_parking_places | double precision | YES
- raw_real_estate | nb_boxes | double precision | YES
- raw_real_estate | nb_photos | double precision | YES
- raw_real_estate | has_a_balcony | double precision | YES
- raw_real_estate | nb_terraces | double precision | YES
- raw_real_estate | has_a_cellar | double precision | YES
- raw_real_estate | has_a_garage | double precision | YES
- raw_real_estate | has_air_conditioning | double precision | YES
- raw_real_estate | last_floor | double precision | YES
- raw_real_estate | upper_floors | double precision | YES
- raw_real_estate | price | double precision | NO
- raw_real_estate | ingest_date | date | YES

## CONSTRAINTS

- ingestion_log | CHECK | None | ingestion_log | file_type
- ingestion_log | CHECK | None | None | None
- ingestion_log | CHECK | None | None | None
- ingestion_log | PRIMARY KEY | id | ingestion_log | id
- raw_real_estate | CHECK | None | None | None
- raw_real_estate | CHECK | None | None | None
- raw_real_estate | PRIMARY KEY | id_annonce | raw_real_estate | id_annonce