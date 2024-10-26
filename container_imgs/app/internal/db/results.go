package db

type UserCumPoints struct {
	UserName         string `json:"user_name"`
	CumulativePoints []int  `json:"cumulative_points"`
}

func GetUserPoints() ([]UserCumPoints, error) {
	db := New()
	rows, err := db.Query(
		`WITH user_points AS (
			SELECT
				user_id,
				matchday,
				SUM(points) OVER (
					PARTITION BY user_id
					ORDER BY matchday
					ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
				) AS cumulative_points
			FROM
				bavariada.results
		)
		SELECT
			users.raw_user_meta_data->>'display_name' AS user_name,
			array_agg(points.cumulative_points::integer ORDER BY points.matchday) AS cumulative_points
		FROM
			user_points points
		INNER JOIN
			auth.users users ON points.user_id = users.id
		GROUP BY
			points.user_id, users.raw_user_meta_data->>'display_name';`,
	)
	if err != nil {
		return []UserCumPoints{}, err
	}

	userPoints := []UserCumPoints{}
	for rows.Next() {
		userPoint := UserCumPoints{}
		err = rows.Scan(&userPoint.UserName, &userPoint.CumulativePoints)
		if err != nil {
			return []UserCumPoints{}, err
		}
		userPoints = append(userPoints, userPoint)
	}
	return userPoints, nil
}

type UserTotalResults struct {
	UserName    string  `json:"user_name"`
	TotalPoints int     `json:"total_points"`
	TotalPrice  float32 `json:"total_price"`
	TotalDebt   float32 `json:"total_debt"`
}

func GetTotalResults() ([]UserTotalResults, error) {
	db := New()
	rows, err := db.Query(
		`SELECT
			users.raw_user_meta_data->>'display_name' AS user_name,
			SUM(results.points) as total_points,
			SUM(results.price_euros) as price_euros,
			SUM(results.debt_euros) as debt_euros
		FROM
			bavariada.results as results
		INNER JOIN
			auth.users users ON results.user_id = users.id
		GROUP BY
			results.user_id,
			users.raw_user_meta_data->>'display_name'
		ORDER BY
			total_points DESC;`,
	)
	if err != nil {
		return []UserTotalResults{}, err
	}

	userResults := []UserTotalResults{}
	for rows.Next() {
		userPoint := UserTotalResults{}
		err = rows.Scan(&userPoint.UserName, &userPoint.TotalPoints, &userPoint.TotalPrice, &userPoint.TotalDebt)
		if err != nil {
			return []UserTotalResults{}, err
		}
		userResults = append(userResults, userPoint)
	}
	return userResults, nil
}

type UserMatchdayResults struct {
	UserName  string  `json:"user_name"`
	MatchDay  int     `json:"matchday"`
	Points    int     `json:"points"`
	DebtEuros float32 `json:"debt_euros"`
}

func GetResultsPerMatchday() ([]UserMatchdayResults, error) {
	db := New()
	rows, err := db.Query(
		`SELECT
			users.raw_user_meta_data->>'display_name' AS user_name,
			results.matchday,
			results.points,
			results.debt_euros
		FROM
			bavariada.results as results
		INNER JOIN
			auth.users users ON results.user_id = users.id
		ORDER BY
			results.matchday DESC, results.points DESC;`,
	)
	if err != nil {
		return []UserMatchdayResults{}, err
	}

	userResults := []UserMatchdayResults{}
	for rows.Next() {
		userResult := UserMatchdayResults{}
		err = rows.Scan(&userResult.UserName, &userResult.MatchDay, &userResult.Points, &userResult.DebtEuros)
		if err != nil {
			return []UserMatchdayResults{}, err
		}
		userResults = append(userResults, userResult)
	}
	return userResults, nil
}

func GetTotalDebt() (float32, error) {
	db := New()

	var totalDebt float32
	err := db.QueryRow(
		`SELECT
			SUM(results.debt_euros) as debt_euros
		FROM
			bavariada.results as results;`,
	).Scan(&totalDebt)

	if err != nil {
		return 0, err
	}

	return totalDebt, nil
}

func GetTotalPrice() (float32, error) {
	db := New()

	var totalPrice float32
	err := db.QueryRow(
		`SELECT
			SUM(results.price_euros) as price_euros
		FROM
			bavariada.results as results;`,
	).Scan(&totalPrice)

	if err != nil {
		return 0, err
	}

	return totalPrice, nil
}
