-- +goose Up
-- +goose StatementBegin
CREATE TABLE bavariada.predictions (
    user_id UUID NOT NULL,
    matchday INT NOT NULL,
    predictions CHAR(3)[] NOT NULL,
    PRIMARY KEY (user_id, matchday),
    FOREIGN KEY (matchday) REFERENCES bavariada.matchdays(matchday)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.predictions;
-- +goose StatementEnd
