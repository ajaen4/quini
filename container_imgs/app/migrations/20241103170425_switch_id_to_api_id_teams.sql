-- +goose Up
-- +goose StatementBegin
-- 1. First, temporarily drop the foreign key constraints from matches table
ALTER TABLE bavariada.matches
  DROP CONSTRAINT matches_away_team_id_fkey;

ALTER TABLE bavariada.matches
  DROP CONSTRAINT matches_home_team_id_fkey;

-- 2. Create temporary columns in matches table (without NOT NULL initially)
ALTER TABLE bavariada.matches
  ADD COLUMN temp_home_team_id INTEGER;

ALTER TABLE bavariada.matches
  ADD COLUMN temp_away_team_id INTEGER;

-- 3. Update the temporary columns with the api_id values
UPDATE bavariada.matches m
SET temp_home_team_id = t.api_id
FROM bavariada.teams t
WHERE m.home_team_id = t.id;

UPDATE bavariada.matches m
SET temp_away_team_id = t.api_id
FROM bavariada.teams t
WHERE m.away_team_id = t.id;

-- 4. Now add NOT NULL constraints after data is populated
ALTER TABLE bavariada.matches
  ALTER COLUMN temp_home_team_id SET NOT NULL;

ALTER TABLE bavariada.matches
  ALTER COLUMN temp_away_team_id SET NOT NULL;

-- 5. Drop the primary key constraint from teams table
ALTER TABLE bavariada.teams
  DROP CONSTRAINT teams_pkey;

-- 6. Modify the teams table columns
ALTER TABLE bavariada.teams
  RENAME COLUMN id TO loterias_id;

ALTER TABLE bavariada.teams
  RENAME COLUMN api_id TO id;

-- 7. Add the new primary key constraint on the id column (formerly api_id)
ALTER TABLE bavariada.teams
  ADD CONSTRAINT teams_pkey PRIMARY KEY (id);

-- 8. Drop the original columns and rename the temporary columns in matches
ALTER TABLE bavariada.matches
  DROP COLUMN home_team_id;

ALTER TABLE bavariada.matches
  DROP COLUMN away_team_id;

ALTER TABLE bavariada.matches
  RENAME COLUMN temp_home_team_id TO home_team_id;

ALTER TABLE bavariada.matches
  RENAME COLUMN temp_away_team_id TO away_team_id;

-- 9. Recreate the foreign key constraints with the new column types
ALTER TABLE bavariada.matches
  ADD CONSTRAINT matches_home_team_id_fkey
    FOREIGN KEY (home_team_id) REFERENCES bavariada.teams (id);

ALTER TABLE bavariada.matches
  ADD CONSTRAINT matches_away_team_id_fkey
    FOREIGN KEY (away_team_id) REFERENCES bavariada.teams (id);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
-- 1. Drop the foreign key constraints
ALTER TABLE bavariada.matches
  DROP CONSTRAINT matches_away_team_id_fkey;

ALTER TABLE bavariada.matches
  DROP CONSTRAINT matches_home_team_id_fkey;

-- 2. Create temporary columns for the reverse migration
ALTER TABLE bavariada.matches
  ADD COLUMN temp_home_team_id VARCHAR(50);

ALTER TABLE bavariada.matches
  ADD COLUMN temp_away_team_id VARCHAR(50);

-- 3. Update the temporary columns with the loterias_id values
UPDATE bavariada.matches m
SET temp_home_team_id = t.loterias_id
FROM bavariada.teams t
WHERE m.home_team_id = t.id;

UPDATE bavariada.matches m
SET temp_away_team_id = t.loterias_id
FROM bavariada.teams t
WHERE m.away_team_id = t.id;

-- 4. Add NOT NULL constraints after data is populated
ALTER TABLE bavariada.matches
  ALTER COLUMN temp_home_team_id SET NOT NULL;

ALTER TABLE bavariada.matches
  ALTER COLUMN temp_away_team_id SET NOT NULL;

-- 5. Drop the primary key constraint from teams table
ALTER TABLE bavariada.teams
  DROP CONSTRAINT teams_pkey;

-- 6. Rename the columns back to their original names
ALTER TABLE bavariada.teams
  RENAME COLUMN id TO api_id;

ALTER TABLE bavariada.teams
  RENAME COLUMN loterias_id TO id;

-- 7. Recreate the original primary key constraint
ALTER TABLE bavariada.teams
  ADD CONSTRAINT teams_pkey PRIMARY KEY (id);

-- 8. Drop the current columns and rename the temporary columns
ALTER TABLE bavariada.matches
  DROP COLUMN home_team_id;

ALTER TABLE bavariada.matches
  DROP COLUMN away_team_id;

ALTER TABLE bavariada.matches
  RENAME COLUMN temp_home_team_id TO home_team_id;

ALTER TABLE bavariada.matches
  RENAME COLUMN temp_away_team_id TO away_team_id;

-- 9. Recreate the original foreign key constraints
ALTER TABLE bavariada.matches
  ADD CONSTRAINT matches_home_team_id_fkey
    FOREIGN KEY (home_team_id) REFERENCES bavariada.teams (id);

ALTER TABLE bavariada.matches
  ADD CONSTRAINT matches_away_team_id_fkey
    FOREIGN KEY (away_team_id) REFERENCES bavariada.teams (id);
-- +goose StatementEnd
