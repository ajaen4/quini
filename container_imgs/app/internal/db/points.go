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
			bavariada.points
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

type UserTotalPoints struct {
	UserName    string `json:"user_name"`
	TotalPoints int    `json:"total_points"`
}

func GetTotalPoints() ([]UserTotalPoints, error) {
	db := New()
	rows, err := db.Query(
		`SELECT
			users.raw_user_meta_data->>'display_name' AS user_name,
			SUM(points.points) as total_points
		FROM 
			bavariada.points as points
		INNER JOIN
			auth.users users ON points.user_id = users.id
		GROUP BY 
			points.user_id,
			users.raw_user_meta_data->>'display_name'
		ORDER BY 
			total_points DESC;`,
	)
	if err != nil {
		return []UserTotalPoints{}, err
	}

	userPoints := []UserTotalPoints{}
	for rows.Next() {
		userPoint := UserTotalPoints{}
		err = rows.Scan(&userPoint.UserName, &userPoint.TotalPoints)
		if err != nil {
			return []UserTotalPoints{}, err
		}
		userPoints = append(userPoints, userPoint)
	}
	return userPoints, nil
}

type UserMatchdayPoints struct {
	UserName string `json:"user_name"`
	MatchDay int    `json:"matchday"`
	Points   int    `json:"points"`
}

func GetPointsPerMatchday() ([]UserMatchdayPoints, error) {
	db := New()
	rows, err := db.Query(
		`SELECT
			users.raw_user_meta_data->>'display_name' AS user_name,
			points.matchday,
			points.points
		FROM 
			bavariada.points as points
		INNER JOIN
			auth.users users ON points.user_id = users.id
		ORDER BY 
			points.matchday DESC, points.points DESC;`,
	)
	if err != nil {
		return []UserMatchdayPoints{}, err
	}

	userPoints := []UserMatchdayPoints{}
	for rows.Next() {
		userPoint := UserMatchdayPoints{}
		err = rows.Scan(&userPoint.UserName, &userPoint.MatchDay, &userPoint.Points)
		if err != nil {
			return []UserMatchdayPoints{}, err
		}
		userPoints = append(userPoints, userPoint)
	}
	return userPoints, nil
}
