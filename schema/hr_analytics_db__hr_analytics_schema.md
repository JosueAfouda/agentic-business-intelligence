# Schéma de la base hr_analytics_db (Schema: hr_analytics)

_Note : seules les tables physiques (BASE TABLE) sont prises en compte. Les vues SQL sont volontairement exclues._


## TABLES

- hr_analytics.dim_date
- hr_analytics.dim_education_level
- hr_analytics.dim_employee
- hr_analytics.dim_rating_level
- hr_analytics.dim_satisfaction
- hr_analytics.fact_performance

## COLUMNS

- hr_analytics.dim_date | date_key | date | NO
- hr_analytics.dim_date | year | integer | YES
- hr_analytics.dim_date | quarter | integer | YES
- hr_analytics.dim_date | month | integer | YES
- hr_analytics.dim_date | month_name | character varying | YES
- hr_analytics.dim_date | week_of_year | integer | YES
- hr_analytics.dim_date | day | integer | YES
- hr_analytics.dim_date | day_name | character varying | YES
- hr_analytics.dim_education_level | education_level_id | integer | NO
- hr_analytics.dim_education_level | education_level | character varying | NO
- hr_analytics.dim_employee | employee_id | character varying | NO
- hr_analytics.dim_employee | first_name | character varying | YES
- hr_analytics.dim_employee | last_name | character varying | YES
- hr_analytics.dim_employee | gender | character varying | YES
- hr_analytics.dim_employee | age | integer | YES
- hr_analytics.dim_employee | business_travel | character varying | YES
- hr_analytics.dim_employee | department | character varying | YES
- hr_analytics.dim_employee | distance_from_home_km | integer | YES
- hr_analytics.dim_employee | state | character varying | YES
- hr_analytics.dim_employee | ethnicity | character varying | YES
- hr_analytics.dim_employee | education_level_id | integer | YES
- hr_analytics.dim_employee | education_field | character varying | YES
- hr_analytics.dim_employee | job_role | character varying | YES
- hr_analytics.dim_employee | marital_status | character varying | YES
- hr_analytics.dim_employee | salary | integer | YES
- hr_analytics.dim_employee | stock_option_level | integer | YES
- hr_analytics.dim_employee | overtime | character varying | YES
- hr_analytics.dim_employee | hire_date | date | YES
- hr_analytics.dim_employee | attrition | character varying | YES
- hr_analytics.dim_employee | years_at_company | integer | YES
- hr_analytics.dim_employee | years_in_most_recent_role | integer | YES
- hr_analytics.dim_employee | years_since_last_promotion | integer | YES
- hr_analytics.dim_employee | years_with_curr_manager | integer | YES
- hr_analytics.dim_rating_level | rating_id | integer | NO
- hr_analytics.dim_rating_level | rating_level | character varying | NO
- hr_analytics.dim_satisfaction | satisfaction_id | integer | NO
- hr_analytics.dim_satisfaction | satisfaction_level | character varying | NO
- hr_analytics.fact_performance | performance_id | character varying | NO
- hr_analytics.fact_performance | employee_id | character varying | YES
- hr_analytics.fact_performance | review_date | date | YES
- hr_analytics.fact_performance | environment_satisfaction | integer | YES
- hr_analytics.fact_performance | job_satisfaction | integer | YES
- hr_analytics.fact_performance | relationship_satisfaction | integer | YES
- hr_analytics.fact_performance | training_opportunities_within_year | integer | YES
- hr_analytics.fact_performance | training_opportunities_taken | integer | YES
- hr_analytics.fact_performance | work_life_balance | integer | YES
- hr_analytics.fact_performance | self_rating | integer | YES
- hr_analytics.fact_performance | manager_rating | integer | YES

## CONSTRAINTS

- hr_analytics.dim_date | CHECK | None | None | None
- hr_analytics.dim_date | PRIMARY KEY | date_key | hr_analytics.dim_date | date_key
- hr_analytics.dim_education_level | CHECK | None | None | None
- hr_analytics.dim_education_level | CHECK | None | None | None
- hr_analytics.dim_education_level | PRIMARY KEY | education_level_id | hr_analytics.dim_education_level | education_level_id
- hr_analytics.dim_employee | CHECK | None | None | None
- hr_analytics.dim_employee | FOREIGN KEY | education_level_id | hr_analytics.dim_education_level | education_level_id
- hr_analytics.dim_employee | PRIMARY KEY | employee_id | hr_analytics.dim_employee | employee_id
- hr_analytics.dim_rating_level | CHECK | None | None | None
- hr_analytics.dim_rating_level | CHECK | None | None | None
- hr_analytics.dim_rating_level | PRIMARY KEY | rating_id | hr_analytics.dim_rating_level | rating_id
- hr_analytics.dim_satisfaction | CHECK | None | None | None
- hr_analytics.dim_satisfaction | CHECK | None | None | None
- hr_analytics.dim_satisfaction | PRIMARY KEY | satisfaction_id | hr_analytics.dim_satisfaction | satisfaction_id
- hr_analytics.fact_performance | CHECK | None | None | None
- hr_analytics.fact_performance | FOREIGN KEY | employee_id | hr_analytics.dim_employee | employee_id
- hr_analytics.fact_performance | FOREIGN KEY | environment_satisfaction | hr_analytics.dim_satisfaction | satisfaction_id
- hr_analytics.fact_performance | FOREIGN KEY | relationship_satisfaction | hr_analytics.dim_satisfaction | satisfaction_id
- hr_analytics.fact_performance | FOREIGN KEY | self_rating | hr_analytics.dim_rating_level | rating_id
- hr_analytics.fact_performance | FOREIGN KEY | manager_rating | hr_analytics.dim_rating_level | rating_id
- hr_analytics.fact_performance | FOREIGN KEY | review_date | hr_analytics.dim_date | date_key
- hr_analytics.fact_performance | FOREIGN KEY | job_satisfaction | hr_analytics.dim_satisfaction | satisfaction_id
- hr_analytics.fact_performance | PRIMARY KEY | performance_id | hr_analytics.fact_performance | performance_id