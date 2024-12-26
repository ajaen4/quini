-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.matchdays ADD COLUMN sorteo_id INT NULL;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.matchdays DROP COLUMN sorteo_id;
-- +goose StatementEnd
