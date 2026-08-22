-- ============================================================
-- CreditPulse
-- Snowflake Bootstrap Script
-- ============================================================
-- Purpose:
--   Creates the foundational Snowflake resources required
--   for the CreditPulse data platform.
--
-- Environment:
--   Development / Portfolio
--
-- Note:
--   Administrative statements in this script require
--   ACCOUNTADMIN or another appropriately privileged role.
-- ============================================================


-- ------------------------------------------------------------
-- 1. Administrative context
-- ------------------------------------------------------------

USE ROLE ACCOUNTADMIN;


-- ------------------------------------------------------------
-- 2. Virtual warehouse
-- ------------------------------------------------------------

CREATE WAREHOUSE IF NOT EXISTS CREDITPULSE_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Compute warehouse for CreditPulse development';

-- Enforce expected warehouse configuration even when the warehouse
-- already exists.
ALTER WAREHOUSE CREDITPULSE_WH SET
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
-- ------------------------------------------------------------
-- 3. Project database
-- ------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS CREDITPULSE
    COMMENT = 'Primary database for the CreditPulse data platform';

-- ------------------------------------------------------------
-- 4. Project schemas
-- ------------------------------------------------------------

USE DATABASE CREDITPULSE;

CREATE SCHEMA IF NOT EXISTS RAW
    COMMENT = 'Bronze layer: source-aligned raw ingestion data';

CREATE SCHEMA IF NOT EXISTS CORE
    COMMENT = 'Silver layer: cleaned, standardized, and conformed data';

CREATE SCHEMA IF NOT EXISTS ANALYTICS
    COMMENT = 'Gold layer: dimensional models and business-facing marts';

CREATE SCHEMA IF NOT EXISTS CONTROL
    COMMENT = 'Pipeline execution metadata, audit records, and watermarks';

CREATE SCHEMA IF NOT EXISTS QUALITY
    COMMENT = 'Data quality results, rejected records, and quarantine data';

-- ------------------------------------------------------------
-- 5. CreditPulse engineering role
-- ------------------------------------------------------------

CREATE ROLE IF NOT EXISTS CREDITPULSE_ENGINEER_ROLE
    COMMENT = 'Primary development role for the CreditPulse data platform';

-- Keep the custom role within Snowflake's normal role hierarchy.
GRANT ROLE CREDITPULSE_ENGINEER_ROLE TO ROLE SYSADMIN;

-- User assignment is environment-specific.
-- Run separately for the appropriate Snowflake user:
--
-- GRANT ROLE CREDITPULSE_ENGINEER_ROLE TO USER <SNOWFLAKE_USER>;

-- ------------------------------------------------------------
-- 6. Role grants
-- ------------------------------------------------------------

-- Warehouse access
GRANT USAGE
ON WAREHOUSE CREDITPULSE_WH
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- Database access
GRANT USAGE
ON DATABASE CREDITPULSE
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- Schema access
GRANT USAGE ON SCHEMA CREDITPULSE.RAW
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT USAGE ON SCHEMA CREDITPULSE.CORE
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT USAGE ON SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT USAGE ON SCHEMA CREDITPULSE.CONTROL
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT USAGE ON SCHEMA CREDITPULSE.QUALITY
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- ------------------------------------------------------------
-- 7. Object creation privileges
-- ------------------------------------------------------------

-- RAW: ingestion layer
GRANT CREATE TABLE
ON SCHEMA CREDITPULSE.RAW
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT CREATE STAGE
ON SCHEMA CREDITPULSE.RAW
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT CREATE FILE FORMAT
ON SCHEMA CREDITPULSE.RAW
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- CORE: dbt Silver layer
GRANT CREATE TABLE
ON SCHEMA CREDITPULSE.CORE
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT CREATE VIEW
ON SCHEMA CREDITPULSE.CORE
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- ANALYTICS: Gold / marts
GRANT CREATE TABLE
ON SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT CREATE VIEW
ON SCHEMA CREDITPULSE.ANALYTICS
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- CONTROL: pipeline metadata
GRANT CREATE TABLE
ON SCHEMA CREDITPULSE.CONTROL
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT CREATE VIEW
ON SCHEMA CREDITPULSE.CONTROL
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- QUALITY: validation / quarantine
GRANT CREATE TABLE
ON SCHEMA CREDITPULSE.QUALITY
TO ROLE CREDITPULSE_ENGINEER_ROLE;

GRANT CREATE VIEW
ON SCHEMA CREDITPULSE.QUALITY
TO ROLE CREDITPULSE_ENGINEER_ROLE;

-- ------------------------------------------------------------
-- 8. Verification
-- ------------------------------------------------------------

USE ROLE CREDITPULSE_ENGINEER_ROLE;
USE WAREHOUSE CREDITPULSE_WH;
USE DATABASE CREDITPULSE;
USE SCHEMA RAW;

SELECT
    CURRENT_USER()      AS current_user,
    CURRENT_ROLE()      AS current_role,
    CURRENT_WAREHOUSE() AS current_warehouse,
    CURRENT_DATABASE()  AS current_database,
    CURRENT_SCHEMA()    AS current_schema;