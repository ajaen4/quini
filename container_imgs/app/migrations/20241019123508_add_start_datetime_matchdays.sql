-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.matchdays
ADD COLUMN start_datetime TIMESTAMP;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.matchdays
DROP COLUMN start_datetime;
-- +goose StatementEnd
