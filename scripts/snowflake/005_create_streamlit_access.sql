-- ============================================================
-- CreditPulse
-- Streamlit Deployment Access
-- ============================================================
-- Purpose:
--   Creates isolated, least-privilege Snowflake resources for
--   the public CreditPulse Streamlit application.
--
-- Security model:
--   - Dedicated compute warehouse
--   - Dedicated read-only role
--   - ANALYTICS read access only
--   - CONTROL access limited to PIPELINE_RUNS
--   - No access to RAW, CORE, or QUALITY
--   - No CREATE / INSERT / UPDATE / DELETE privileges
-- ============================================================


-- ------------------------------------------------------------
-- 1. Administrative context
-- ------------------------------------------------------------

USE ROLE ACCOUNTADMIN;


-- ------------------------------------------------------------
-- 2. Dedicated Streamlit warehouse
-- ------------------------------------------------------------

CREATE WAREHOUSE IF NOT EXISTS CREDITPULSE_STREAMLIT_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Dedicated compute warehouse for the CreditPulse Streamlit application';


ALTER WAREHOUSE CREDITPULSE_STREAMLIT_WH SET
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;


-- ------------------------------------------------------------
-- 3. Dedicated read-only application role
-- ------------------------------------------------------------

CREATE ROLE IF NOT EXISTS CREDITPULSE_STREAMLIT_ROLE
    COMMENT = 'Least-privilege read-only role for the CreditPulse Streamlit application';


-- Keep the custom role within Snowflake's standard role hierarchy.
GRANT ROLE CREDITPULSE_STREAMLIT_ROLE
TO ROLE SYSADMIN;


-- ------------------------------------------------------------
-- 4. Warehouse access
-- ------------------------------------------------------------

GRANT USAGE
ON WAREHOUSE CREDITPULSE_STREAMLIT_WH
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- ------------------------------------------------------------
-- 5. Database access
-- ------------------------------------------------------------

GRANT USAGE
ON DATABASE CREDITPULSE
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- ------------------------------------------------------------
-- 6. Analytics schema access
-- ------------------------------------------------------------

GRANT USAGE
ON SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- Existing Gold tables
GRANT SELECT
ON ALL TABLES IN SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- Existing Gold views
GRANT SELECT
ON ALL VIEWS IN SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- Preserve read access when dbt creates future Gold tables.
GRANT SELECT
ON FUTURE TABLES IN SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- Preserve read access when dbt creates future Gold views.
GRANT SELECT
ON FUTURE VIEWS IN SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- ------------------------------------------------------------
-- 7. CONTROL access
-- ------------------------------------------------------------
-- The dashboard only needs pipeline execution metadata.
-- Do not grant blanket CONTROL schema table access.

GRANT USAGE
ON SCHEMA CREDITPULSE.CONTROL
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


GRANT SELECT
ON TABLE CREDITPULSE.CONTROL.PIPELINE_RUNS
TO ROLE CREDITPULSE_STREAMLIT_ROLE;


-- ------------------------------------------------------------
-- 8. Verification
-- ------------------------------------------------------------

USE ROLE CREDITPULSE_STREAMLIT_ROLE;
USE WAREHOUSE CREDITPULSE_STREAMLIT_WH;
USE DATABASE CREDITPULSE;
USE SCHEMA ANALYTICS;


SELECT
    CURRENT_ROLE()      AS current_role,
    CURRENT_WAREHOUSE() AS current_warehouse,
    CURRENT_DATABASE()  AS current_database,
    CURRENT_SCHEMA()    AS current_schema;


-- Verify dashboard-readable ANALYTICS data.
SELECT COUNT(*) AS company_count
FROM CREDITPULSE.ANALYTICS.DIM_COMPANY;


SELECT COUNT(*) AS liquidity_row_count
FROM CREDITPULSE.ANALYTICS.MART_COMPANY_LIQUIDITY;


SELECT COUNT(*) AS performance_row_count
FROM CREDITPULSE.ANALYTICS.MART_COMPANY_PERFORMANCE;


SELECT COUNT(*) AS macro_row_count
FROM CREDITPULSE.ANALYTICS.MART_MACRO_ENVIRONMENT;


SELECT COUNT(*) AS treasury_row_count
FROM CREDITPULSE.ANALYTICS.MART_TREASURY_YIELD_CURVE;


-- Verify dashboard-readable operational metadata.
SELECT COUNT(*) AS pipeline_run_count
FROM CREDITPULSE.CONTROL.PIPELINE_RUNS;