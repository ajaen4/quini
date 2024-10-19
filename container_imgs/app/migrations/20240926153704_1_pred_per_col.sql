-- +goose Up
-- SQL in this section is executed when the migration is applied.
BEGIN;

-- Create a temporary table to hold the transformed data
CREATE TEMPORARY TABLE temp_predictions AS
SELECT
    p.user_id,
    p.season,
    p.matchday,
    p.match_num,
    v.rn - 1 AS col_num,
    CASE
        WHEN p.match_num = 14 THEN p.predictions
        ELSE v.value
    END AS prediction
FROM
    bavariada.predictions p
CROSS JOIN LATERAL (
    SELECT
        row_number() OVER () AS rn,
        CASE
            WHEN p.match_num = 14 THEN p.predictions
            ELSE trim(unnest)
        END AS value
    FROM unnest(string_to_array(p.predictions, '-'))
) v;

-- Clear existing data from the altered table
DELETE FROM bavariada.predictions;

-- Alter the existing table to match the new structure
ALTER TABLE bavariada.predictions
DROP CONSTRAINT predictions_pkey,
DROP CONSTRAINT predictions_season_matchday_match_num_fkey,
DROP COLUMN predictions,
ADD COLUMN col_num INTEGER,
ADD COLUMN prediction CHARACTER VARYING(10);

-- Insert transformed data into the altered table
INSERT INTO bavariada.predictions (user_id, season, matchday, match_num, col_num, prediction)
SELECT user_id, season, matchday, match_num, col_num, prediction
FROM temp_predictions;

-- Add new primary key and foreign key constraints
ALTER TABLE bavariada.predictions
ADD PRIMARY KEY (user_id, season, matchday, match_num, col_num),
ADD CONSTRAINT predictions_season_matchday_match_num_fkey
FOREIGN KEY (season, matchday, match_num)
REFERENCES bavariada.matches (season, matchday, match_num);

-- Drop the temporary table
DROP TABLE temp_predictions;

COMMIT;

-- +goose Down
-- SQL in this section is executed when the migration is rolled back.
BEGIN;

-- Create a temporary table to hold the consolidated data
CREATE TEMPORARY TABLE temp_predictions AS
SELECT
    user_id,
    season,
    matchday,
    match_num,
    CASE
        WHEN match_num = 14 THEN MAX(prediction)
        ELSE string_agg(prediction, '-' ORDER BY col_num)
    END AS predictions
FROM
    bavariada.predictions
GROUP BY
    user_id, season, matchday, match_num;

-- Alter the table back to its original structure
ALTER TABLE bavariada.predictions
DROP CONSTRAINT predictions_pkey,
DROP CONSTRAINT predictions_season_matchday_match_num_fkey,
DROP COLUMN col_num,
DROP COLUMN prediction,
ADD COLUMN predictions CHARACTER VARYING(10);

-- Clear existing data from the altered table
DELETE FROM bavariada.predictions;

-- Insert consolidated data back into the table
INSERT INTO bavariada.predictions (user_id, season, matchday, match_num, predictions)
SELECT user_id, season, matchday, match_num, predictions
FROM temp_predictions;

-- Re-add original constraints
ALTER TABLE bavariada.predictions
ADD PRIMARY KEY (user_id, season, matchday, match_num),
ADD CONSTRAINT predictions_season_matchday_match_num_fkey
FOREIGN KEY (season, matchday, match_num)
REFERENCES bavariada.matches (season, matchday, match_num);

-- Drop the temporary table
DROP TABLE temp_predictions;

COMMIT;
