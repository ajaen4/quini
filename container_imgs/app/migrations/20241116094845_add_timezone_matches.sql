-- +goose Up
-- +goose StatementBegin

ALTER TABLE bavariada.matches ADD COLUMN kickoff_datetime_tz timestamptz;
UPDATE bavariada.matches SET kickoff_datetime_tz = kickoff_datetime AT TIME ZONE 'Europe/Madrid';
ALTER TABLE bavariada.matches DROP COLUMN kickoff_datetime;
ALTER TABLE bavariada.matches RENAME COLUMN kickoff_datetime_tz TO kickoff_datetime;

ALTER TABLE bavariada.matches ADD COLUMN status VARCHAR(4);
ALTER TABLE bavariada.matches ADD COLUMN home_goals INT;
ALTER TABLE bavariada.matches ADD COLUMN away_goals INT;

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

ALTER TABLE bavariada.matches ADD COLUMN kickoff_datetime_no_tz timestamp without time zone;
UPDATE bavariada.matches
SET kickoff_datetime_no_tz = kickoff_datetime AT TIME ZONE 'Europe/Madrid';
ALTER TABLE bavariada.matches DROP COLUMN kickoff_datetime;
ALTER TABLE bavariada.matches RENAME COLUMN kickoff_datetime_no_tz TO kickoff_datetime;

ALTER TABLE bavariada.matches DROP COLUMN status;
ALTER TABLE bavariada.matches DROP COLUMN home_goals;
ALTER TABLE bavariada.matches DROP COLUMN away_goals;

-- +goose StatementEnd
