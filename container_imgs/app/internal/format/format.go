package format

import (
	"app/internal/db"
	"fmt"
	"strconv"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
)

func FormatMatchDateTime(datetime time.Time) string {
	madridLoc, err := time.LoadLocation("Europe/Madrid")
	if err != nil {
		return "Error loading timezone"
	}

	madridTime := datetime.In(madridLoc)
	spanishDayNames := map[string]string{
		"Mon": "Lun",
		"Tue": "Mar",
		"Wed": "Mié",
		"Thu": "Jue",
		"Fri": "Vie",
		"Sat": "Sáb",
		"Sun": "Dom",
	}

	engDay := madridTime.Format("Mon")
	spanishDay := spanishDayNames[engDay]
	return spanishDay + " " + madridTime.Format("15:04")
}

func FormatGoals(goals pgtype.Int4) string {
	if goals.Valid {
		return strconv.Itoa(int(goals.Int32))
	}
	return "0"
}

func FormatMins(match db.Match) string {
	if match.Status == "HT" {
		return "DES"
	}
	if match.Status == "FT" {
		return "FIN"
	}

	var valMins int
	mins := match.Minutes
	if mins.Valid {
		valMins = int(mins.Int32)
	} else {
		valMins = 0
	}
	return fmt.Sprintf("%s'", strconv.Itoa(valMins))
}
