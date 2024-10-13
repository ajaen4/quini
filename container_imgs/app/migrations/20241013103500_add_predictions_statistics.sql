-- +goose Up
-- +goose StatementBegin
CREATE TABLE bavariada.predictions_stats (
    season CHAR(9) NOT NULL,
    matchday INT NOT NULL,
    match_num INT NOT NULL,
    home_percent INT NOT NULL,
    draw_percent INT NOT NULL,
    away_percent INT NOT NULL,
    PRIMARY KEY (season, matchday, match_num),
    FOREIGN KEY (season, matchday, match_num) REFERENCES bavariada.matches(season, matchday, match_num)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.predictions_stats;
-- +goose StatementEnd
