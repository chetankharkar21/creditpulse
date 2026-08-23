-- ============================================================
-- CreditPulse
-- Pipeline Control / Observability
-- ============================================================
-- Purpose:
--   Stores one audit record for every end-to-end CreditPulse
--   pipeline execution.
--
-- Status lifecycle:
--   RUNNING -> SUCCESS
--   RUNNING -> FAILED
-- ============================================================

USE ROLE CREDITPULSE_ENGINEER_ROLE;
USE WAREHOUSE CREDITPULSE_WH;
USE DATABASE CREDITPULSE;
USE SCHEMA CONTROL;


CREATE TABLE IF NOT EXISTS CREDITPULSE.CONTROL.PIPELINE_RUNS (
    RUN_ID                  VARCHAR(36)      NOT NULL,
    PIPELINE_NAME           VARCHAR(100)     NOT NULL,
    STATUS                  VARCHAR(20)      NOT NULL,

    STARTED_AT              TIMESTAMP_TZ     NOT NULL,
    FINISHED_AT             TIMESTAMP_TZ,
    DURATION_SECONDS        NUMBER(12, 3),

    EXECUTION_ENVIRONMENT   VARCHAR(50)      NOT NULL,
    TRIGGER_TYPE            VARCHAR(50),

    GIT_SHA                 VARCHAR(64),
    GITHUB_RUN_ID           VARCHAR(100),

    ERROR_MESSAGE           VARCHAR,

    CREATED_AT              TIMESTAMP_TZ     NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT              TIMESTAMP_TZ     NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Audit history for end-to-end CreditPulse pipeline executions';


-- ============================================================
-- Verification
-- ============================================================

DESCRIBE TABLE CREDITPULSE.CONTROL.PIPELINE_RUNS;