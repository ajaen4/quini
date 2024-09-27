-- +goose Up
-- SQL in this section is executed when the migration is applied.

-- Rename the table
ALTER TABLE bavariada.results RENAME TO results;

-- Add the new column
ALTER TABLE bavariada.results ADD COLUMN price_euros FLOAT;

-- Update the constraint names to reflect the new table name
ALTER TABLE bavariada.results RENAME CONSTRAINT points_pkey TO results_pkey;
ALTER TABLE bavariada.results RENAME CONSTRAINT points_season_matchday_fkey TO results_season_matchday_fkey;
ALTER TABLE bavariada.results RENAME CONSTRAINT points_user_id_fkey TO results_user_id_fkey;

-- +goose Down
-- SQL in this section is executed when the migration is rolled back.

-- Remove the new column
ALTER TABLE bavariada.results DROP COLUMN price_euros;

-- Rename the table back
ALTER TABLE bavariada.results RENAME TO points;

-- Revert the constraint names
ALTER TABLE bavariada.results RENAME CONSTRAINT results_pkey TO points_pkey;
ALTER TABLE bavariada.results RENAME CONSTRAINT results_season_matchday_fkey TO points_season_matchday_fkey;
ALTER TABLE bavariada.results RENAME CONSTRAINT results_user_id_fkey TO points_user_id_fkey;
