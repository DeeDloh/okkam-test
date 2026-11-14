BEGIN;
CREATE MATERIALIZED VIEW IF NOT EXISTS respondent_stats AS
SELECT
    respondent,
    sex,
    MIN(age) as age,
    AVG(weight) AS avg_weight
FROM observations
GROUP BY sex, respondent;

COMMIT;

ANALYZE respondent_stats;