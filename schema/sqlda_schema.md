# Schéma de la base sqlda

_Note : seules les tables physiques (BASE TABLE) sont prises en compte. Les vues SQL sont volontairement exclues._


## TABLES

- closest_dealerships
- countries
- customer_sales
- customer_survey
- customers
- dealerships
- emails
- products
- public_transportation_by_zip
- sales
- salespeople
- top_cities_data

## COLUMNS

- closest_dealerships | customer_id | bigint | YES
- closest_dealerships | dealership_id | bigint | YES
- closest_dealerships | distance | double precision | YES
- countries | key | integer | NO
- countries | name | text | YES
- countries | founding_year | integer | YES
- countries | capital | text | YES
- customer_sales | customer_json | jsonb | YES
- customer_survey | rating | integer | YES
- customer_survey | feedback | text | YES
- customers | customer_id | bigint | YES
- customers | title | text | YES
- customers | first_name | text | YES
- customers | last_name | text | YES
- customers | suffix | text | YES
- customers | email | text | YES
- customers | gender | text | YES
- customers | ip_address | text | YES
- customers | phone | text | YES
- customers | street_address | text | YES
- customers | city | text | YES
- customers | state | text | YES
- customers | postal_code | text | YES
- customers | latitude | double precision | YES
- customers | longitude | double precision | YES
- customers | date_added | timestamp without time zone | YES
- dealerships | dealership_id | bigint | YES
- dealerships | street_address | text | YES
- dealerships | city | text | YES
- dealerships | state | text | YES
- dealerships | postal_code | text | YES
- dealerships | latitude | double precision | YES
- dealerships | longitude | double precision | YES
- dealerships | date_opened | timestamp without time zone | YES
- dealerships | date_closed | timestamp without time zone | YES
- emails | email_id | bigint | YES
- emails | customer_id | bigint | YES
- emails | email_subject | text | YES
- emails | opened | text | YES
- emails | clicked | text | YES
- emails | bounced | text | YES
- emails | sent_date | timestamp without time zone | YES
- emails | opened_date | timestamp without time zone | YES
- emails | clicked_date | timestamp without time zone | YES
- products | product_id | bigint | YES
- products | model | text | YES
- products | year | bigint | YES
- products | product_type | text | YES
- products | base_msrp | numeric | YES
- products | production_start_date | timestamp without time zone | YES
- products | production_end_date | timestamp without time zone | YES
- public_transportation_by_zip | level_0 | bigint | YES
- public_transportation_by_zip | index | bigint | YES
- public_transportation_by_zip | zip_code | text | YES
- public_transportation_by_zip | public_transportation_pct | double precision | YES
- public_transportation_by_zip | public_transportation_population | bigint | YES
- sales | customer_id | bigint | YES
- sales | product_id | bigint | YES
- sales | sales_transaction_date | timestamp without time zone | YES
- sales | sales_amount | double precision | YES
- sales | channel | text | YES
- sales | dealership_id | double precision | YES
- salespeople | salesperson_id | bigint | YES
- salespeople | dealership_id | bigint | YES
- salespeople | title | text | YES
- salespeople | first_name | text | YES
- salespeople | last_name | text | YES
- salespeople | suffix | text | YES
- salespeople | username | text | YES
- salespeople | gender | text | YES
- salespeople | hire_date | timestamp without time zone | YES
- salespeople | termination_date | timestamp without time zone | YES
- top_cities_data | city | text | YES
- top_cities_data | number_of_customers | bigint | YES
- top_cities_data | female | bigint | YES
- top_cities_data | male | bigint | YES

## CONSTRAINTS

- countries | CHECK | None | None | None
- countries | PRIMARY KEY | key | countries | key
- countries | UNIQUE | name | countries | name