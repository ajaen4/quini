-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.predictions
ADD COLUMN is_correct boolean;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.predictions
DROP COLUMN is_correct boolean;
-- +goose StatementEnd
