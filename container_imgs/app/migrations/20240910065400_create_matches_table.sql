-- +goose Up
-- +goose StatementBegin
CREATE SCHEMA bavariada;

CREATE TYPE status AS ENUM ('IN_PROGRESS', 'FINISHED');

CREATE TABLE bavariada.matchdays (
    matchday INT NOT NULL PRIMARY KEY,
    status status NOT NULL DEFAULT 'IN_PROGRESS'
);

CREATE TABLE bavariada.teams (
    id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    scrapper_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE bavariada.matches (
    id INT NOT NULL,
    league_id INT NOT NULL,
    matchday INT NOT NULL,
    match_num INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (matchday) REFERENCES bavariada.matchdays(matchday),
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
