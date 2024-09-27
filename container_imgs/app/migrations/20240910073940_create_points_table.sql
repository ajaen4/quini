-- +goose Up
-- +goose StatementBegin
CREATE TABLE bavariada.results (
    user_id UUID NOT NULL,
    season CHAR(9) NOT NULL,
    matchday INT NOT NULL,
    points INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, season, matchday),
    FOREIGN KEY (user_id) REFERENCES auth.users(id),
    FOREIGN KEY (season, matchday) REFERENCES bavariada.matchdays(season, matchday)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.results;
-- +goose StatementEnd
