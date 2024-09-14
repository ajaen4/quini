package db

type UserPoints struct {
	UserId      string `json:"user_id"`
	PointsArray []int  `json:"points_array"`
}

func GetUserPoints() ([]UserPoints, error) {
	db := New()
	rows, err := db.Query(
		`SELECT
			user_id,
			array_agg(points ORDER BY matchday) AS points_array
		FROM
    		bavariada.points
		GROUP BY
 	   		user_id;`,
	)
	if err != nil {
		return []UserPoints{}, err
	}

	userPoints := []UserPoints{}
	for rows.Next() {
		userPoint := UserPoints{}
		err = rows.Scan(&userPoint.UserId, &userPoint.PointsArray)
		if err != nil {
			return []UserPoints{}, err
		}
		userPoints = append(userPoints, userPoint)
	}
	return userPoints, nil
}
