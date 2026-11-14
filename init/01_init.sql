BEGIN;

CREATE TABLE observations (
    id INTEGER NOT NULL,
    date DATE NOT NULL,
    respondent INTEGER NOT NULL,
    sex INTEGER NOT NULL CHECK (sex IN (1, 2)),
    age INTEGER NOT NULL CHECK (age >= 0),
    weight DOUBLE PRECISION NOT NULL CHECK (weight >= 0),
    UNIQUE (respondent, date)

);

COPY observations (id, date, respondent, sex, age, weight)
FROM '/data/data.csv'
WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');

UPDATE observations
SET id = id + 1;

ALTER TABLE observations
ADD PRIMARY KEY (id);

COMMIT;

ANALYZE observations;
