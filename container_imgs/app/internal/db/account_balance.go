package db

func UpdateBalance(userId string, amount float64) error {
	db := New()

	_, err := db.Query(`
        UPDATE bavariada.account_balance
        SET balance = balance + $1
        WHERE user_id = $2
    `,
		amount,
		userId,
	)
	if err != nil {
		return err
	}

	return nil
}

func GetBalance(userId string) (float64, error) {
	db := New()

	var balance float64
	err := db.QueryRow(
		`SELECT balance
		FROM bavariada.account_balance
		WHERE user_id = $1;`,
		userId,
	).Scan(&balance)
	if err != nil {
		return 0, err
	}

	return balance, nil
}
