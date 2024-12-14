package db

func GetUsers() (map[string]string, error) {
	db := New()

	rows, err := db.Query(
		`SELECT id, COALESCE(users.raw_user_meta_data->>'display_name', users.email)
		FROM auth.users
		WHERE users.raw_user_meta_data->>'is_auth_user' = 'true';`,
	)
	if err != nil {
		return map[string]string{}, err
	}
	defer rows.Close()

	users := map[string]string{}
	for rows.Next() {
		var userName string
		var userId string
		err = rows.Scan(
			&userId,
			&userName,
		)
		if err != nil {
			return map[string]string{}, err
		}
		users[userId] = userName
	}

	return users, nil
}

func IsAuthUser(id string) (bool, error) {
	db := New()

	var numUsers int
	err := db.QueryRow(
		`SELECT count(*)
			FROM auth.users
			WHERE id = $1 AND raw_user_meta_data->>'is_auth_user' = 'true'`,
		id,
	).Scan(&numUsers)
	if err != nil {
		return false, err
	}

	if numUsers == 1 {
		return true, nil
	}

	return false, nil
}
