-- +goose Up
-- +goose StatementBegin
-- ALTER TABLE bavariada.teams
-- RENAME COLUMN id TO loterias_id;

ALTER TABLE bavariada.teams
ADD COLUMN api_id INT,
ADD COLUMN code CHAR(3),
ADD COLUMN logo_url VARCHAR(200),
ADD COLUMN league_id INT,
DROP COLUMN home_championship;

ALTER TABLE bavariada.matches
ADD COLUMN id INT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.teams
DROP COLUMN api_id,
DROP COLUMN code,
DROP COLUMN logo_url,
DROP COLUMN league_id,
ADD COLUMN home_championship;

ALTER TABLE bavariada.matches
DROP COLUMN id;
-- +goose StatementEnd
