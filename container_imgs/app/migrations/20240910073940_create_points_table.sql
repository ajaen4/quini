-- +goose Up
-- +goose StatementBegin
CREATE TABLE bavariada.points (
    user_id UUID NOT NULL,
    matchday INT NOT NULL,
    points INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, matchday),
    FOREIGN KEY (matchday) REFERENCES bavariada.matchdays(matchday)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.points;
-- +goose StatementEnd
