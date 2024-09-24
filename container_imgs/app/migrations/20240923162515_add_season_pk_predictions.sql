-- +goose Up
-- +goose StatementBegin
ALTER TABLE bavariada.predictions 
DROP CONSTRAINT predictions_pkey,
ADD PRIMARY KEY (user_id, season, matchday, match_num);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE bavariada.predictions 
DROP CONSTRAINT predictions_pkey,
ADD CONSTRAINT predictions_pkey PRIMARY KEY (user_id, matchday, match_num);
-- +goose StatementEnd
