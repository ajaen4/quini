-- +goose Up
-- +goose StatementBegin
ALTER TYPE status ADD VALUE 'NOT_STARTED' BEFORE 'IN_PROGRESS';
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TYPE status DROP VALUE 'NOT_STARTED';
-- +goose StatementEnd
