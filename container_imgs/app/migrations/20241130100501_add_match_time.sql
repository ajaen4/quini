-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.matches ADD COLUMN minutes INT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.matches DROP COLUMN minutes;
-- +goose StatementEnd
