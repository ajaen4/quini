package db

func GetUsers() (map[string]string, error) {
	db := New()

	rows, err := db.Query(
		`SELECT id, users.raw_user_meta_data->>'display_name'
		FROM auth.users;`,
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
