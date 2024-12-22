-- +goose Up
-- +goose StatementBegin
CREATE TABLE bavariada.account_balance (
    user_id UUID NOT NULL,
    balance FLOAT DEFAULT 0,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.account_balance;
-- +goose StatementEnd
