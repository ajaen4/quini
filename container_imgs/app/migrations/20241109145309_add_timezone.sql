-- +goose Up
-- +goose StatementBegin
BEGIN;

ALTER TABLE bavariada.matchdays ADD COLUMN start_datetime_tz timestamptz;
UPDATE bavariada.matchdays SET start_datetime_tz = start_datetime AT TIME ZONE 'Europe/Madrid';
ALTER TABLE bavariada.matchdays DROP COLUMN start_datetime;
ALTER TABLE bavariada.matchdays RENAME COLUMN start_datetime_tz TO start_datetime;

COMMIT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
BEGIN;

ALTER TABLE bavariada.matchdays ADD COLUMN start_datetime_no_tz timestamp without time zone;
UPDATE bavariada.matchdays
SET start_datetime_no_tz = start_datetime AT TIME ZONE 'Europe/Madrid';
ALTER TABLE bavariada.matchdays DROP COLUMN start_datetime;
ALTER TABLE bavariada.matchdays RENAME COLUMN start_datetime_no_tz TO start_datetime;

COMMIT;
-- +goose StatementEnd
