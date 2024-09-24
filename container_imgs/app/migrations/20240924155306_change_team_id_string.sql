-- +goose Up
-- +goose StatementBegin

-- Step 1: Drop foreign key constraints
ALTER TABLE bavariada.matches
DROP CONSTRAINT matches_home_team_id_fkey,
DROP CONSTRAINT matches_away_team_id_fkey;

-- Step 2: Alter the id column in the teams table
ALTER TABLE bavariada.teams
ALTER COLUMN id TYPE VARCHAR(50);

-- Step 3: Alter the corresponding columns in the matches table
ALTER TABLE bavariada.matches
ALTER COLUMN home_team_id TYPE VARCHAR(50),
ALTER COLUMN away_team_id TYPE VARCHAR(50);

-- Step 4: Recreate the foreign key constraints
ALTER TABLE bavariada.matches
ADD CONSTRAINT matches_home_team_id_fkey 
    FOREIGN KEY (home_team_id) REFERENCES bavariada.teams(id),
ADD CONSTRAINT matches_away_team_id_fkey 
    FOREIGN KEY (away_team_id) REFERENCES bavariada.teams(id);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
-- Step 1: Drop foreign key constraints
ALTER TABLE bavariada.matches
DROP CONSTRAINT matches_home_team_id_fkey,
DROP CONSTRAINT matches_away_team_id_fkey;

-- Step 2: Alter the columns in the matches table back to INT
ALTER TABLE bavariada.matches
ALTER COLUMN home_team_id TYPE INT USING home_team_id::integer,
ALTER COLUMN away_team_id TYPE INT USING away_team_id::integer;

-- Step 3: Alter the id column in the teams table back to INT
ALTER TABLE bavariada.teams
ALTER COLUMN id TYPE INT USING id::integer;

-- Step 4: Recreate the foreign key constraints
ALTER TABLE bavariada.matches
ADD CONSTRAINT matches_home_team_id_fkey 
    FOREIGN KEY (home_team_id) REFERENCES bavariada.teams(id),
ADD CONSTRAINT matches_away_team_id_fkey 
    FOREIGN KEY (away_team_id) REFERENCES bavariada.teams(id);
-- +goose StatementEnd
