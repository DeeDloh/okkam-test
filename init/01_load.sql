BEGIN;

COPY observations (id, date, respondent, sex, age, weight)
FROM '/data/data.csv'
WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');


-- Переносим id во временный отрицательный диапазон,
-- чтобы при изменении не было конфликта первичных ключей.
UPDATE observations SET id = -id - 1;
UPDATE observations SET id = -id;

REFRESH MATERIALIZED VIEW public.respondent_stats;

COMMIT;

ANALYZE observations;
ANALYZE respondent_stats;