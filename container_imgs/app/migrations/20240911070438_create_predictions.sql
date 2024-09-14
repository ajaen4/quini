-- +goose Up
-- +goose StatementBegin
CREATE TABLE bavariada.predictions (
    user_id UUID NOT NULL,
    season CHAR(9) NOT NULL,
    matchday INT NOT NULL,
    match_num INT NOT NULL,
    predictions VARCHAR(10) NOT NULL,
    PRIMARY KEY (user_id, matchday, match_num),
    FOREIGN KEY (user_id) REFERENCES auth.users(id),
    FOREIGN KEY (season, matchday, match_num) REFERENCES bavariada.matches(season, matchday, match_num)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.predictions;
-- +goose StatementEnd
