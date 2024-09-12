-- +goose Up
-- +goose StatementBegin
CREATE TABLE quiniela.points (
    user_id UUID NOT NULL,
    matchday INT NOT NULL,
    points INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, matchday),
    FOREIGN KEY (matchday) REFERENCES quiniela.matchdays(matchday)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE quiniela.points;
-- +goose StatementEnd
