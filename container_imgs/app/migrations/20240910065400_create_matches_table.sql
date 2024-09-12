-- +goose Up
-- +goose StatementBegin
CREATE SCHEMA quiniela;

CREATE TYPE status AS ENUM ('IN_PROGRESS', 'FINISHED');

CREATE TABLE quiniela.matchdays (
    matchday INT NOT NULL PRIMARY KEY,
    status status NOT NULL DEFAULT 'IN_PROGRESS'
);

CREATE TABLE quiniela.teams (
    id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    scrapper_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE quiniela.matches (
    id INT NOT NULL,
    league_id INT NOT NULL,
    matchday INT NOT NULL,
    match_num INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (matchday) REFERENCES quiniela.matchdays(matchday),
    FOREIGN KEY (home_team_id) REFERENCES quiniela.teams(id),
    FOREIGN KEY (away_team_id) REFERENCES quiniela.teams(id)
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE quiniela.matches CASCADE;
DROP TABLE quiniela.teams CASCADE;
DROP TABLE quiniela.matchdays CASCADE;
DROP TYPE status;
DROP SCHEMA quiniela;
-- +goose StatementEnd
