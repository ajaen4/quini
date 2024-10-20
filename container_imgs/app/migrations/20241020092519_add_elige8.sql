-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.predictions
ADD COLUMN is_elige8 BOOLEAN DEFAULT FALSE;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.predictions
DROP COLUMN is_elige8;
-- +goose StatementEnd
