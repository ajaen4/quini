-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.results
ADD COLUMN debt_euros FLOAT;

ALTER TABLE bavariada.teams
ADD COLUMN home_championship VARCHAR(50);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.results
DROP COLUMN debt_euros;

ALTER TABLE bavariada.teams
DROP COLUMN home_championship;
-- +goose StatementEnd
