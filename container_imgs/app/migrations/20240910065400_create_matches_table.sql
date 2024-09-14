-- +goose Up
-- +goose StatementBegin
CREATE SCHEMA bavariada;

CREATE TYPE status AS ENUM ('IN_PROGRESS', 'FINISHED');

CREATE TABLE bavariada.matchdays (
    season CHAR(9) NOT NULL,
    matchday INT NOT NULL,
    status status NOT NULL,
    PRIMARY KEY (season, matchday)
);

CREATE TABLE bavariada.teams (
    id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE bavariada.matches (
    season CHAR(9) NOT NULL,
    matchday INT NOT NULL,
    match_num INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (season, matchday, match_num),
    FOREIGN KEY (season, matchday) REFERENCES bavariada.matchdays(season, matchday),
    FOREIGN KEY (home_team_id) REFERENCES bavariada.teams(id),
    FOREIGN KEY (away_team_id) REFERENCES bavariada.teams(id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE bavariada.matches CASCADE;
DROP TABLE bavariada.teams CASCADE;
DROP TABLE bavariada.matchdays CASCADE;
DROP TYPE status;
DROP SCHEMA bavariada;
-- +goose StatementEnd
