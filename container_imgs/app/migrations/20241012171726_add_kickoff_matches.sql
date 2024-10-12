-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.matches
ADD COLUMN kickoff_datetime TIMESTAMP;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.matches
DROP COLUMN kickoff_datetime;
-- +goose StatementEnd
