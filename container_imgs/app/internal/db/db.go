package db

import (
	"aws_lib/aws_lib"
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Service interface {
	Health() map[string]string
	Close() error
	Query(query string, args ...interface{}) (pgx.Rows, error)
	QueryRow(query string, args ...interface{}) pgx.Row
}

type db struct {
	pool     *pgxpool.Pool
	db_name  string
	password string
	username string
	port     string
	host     string
}

var (
	env        = os.Getenv("ENV")
	dbInstance *db
)

func New() Service {
	if dbInstance != nil {
		return dbInstance
	}

	var sslmode string
	var param map[string]string
	var (
		db_name,
		password,
		username,
		port,
		host string
	)

	if env == "LOCAL" {
		db_name = os.Getenv("DB_NAME")
		password = os.Getenv("DB_PASSWORD")
		username = os.Getenv("DB_USERNAME")
		port = os.Getenv("DB_PORT")
		host = os.Getenv("DB_HOST")
	} else {
		sslmode = "require"
		sm := aws_lib.NewSSM("")
		param = sm.GetParam("/bavariada/secrets", true)
		log.Printf("Parameter: %s", param)
		db_name = param["DB_NAME"]
		password = param["DB_PASSWORD"]
		username = param["DB_USERNAME"]
		port = param["DB_PORT"]
		host = param["DB_HOST"]
	}

	log.Println(db_name, password, username, port, host)

	connStr := fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s?sslmode=%s",
		username,
		password,
		host,
		port,
		db_name,
		sslmode,
	)

	config, err := pgxpool.ParseConfig(connStr)
	if err != nil {
		log.Fatalf("Unable to parse connection string: %v", err)
	}

	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %v", err)
	}

	dbInstance = &db{
		pool:     pool,
		db_name:  db_name,
		password: password,
		username: username,
		port:     port,
		host:     host,
	}
	return dbInstance
}

func (db *db) Health() map[string]string {
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	stats := make(map[string]string)

	err := db.pool.Ping(ctx)
	if err != nil {
		stats["status"] = "down"
		stats["error"] = fmt.Sprintf("db down: %v", err)
		log.Fatalf(fmt.Sprintf("db down: %v", err))
		return stats
	}

	stats["status"] = "up"
	stats["message"] = "It's healthy"

	poolStats := db.pool.Stat()
	stats["total_connections"] = strconv.Itoa(int(poolStats.TotalConns()))
	stats["idle_connections"] = strconv.Itoa(int(poolStats.IdleConns()))
	stats["used_connections"] = strconv.Itoa(int(poolStats.AcquiredConns()))

	return stats
}

func (db *db) Close() error {
	log.Printf("Disconnected from db: %s", db.db_name)
	db.pool.Close()
	return nil
}

func (db *db) Query(query string, args ...interface{}) (pgx.Rows, error) {
	return db.pool.Query(context.Background(), query, args...)
}

func (db *db) QueryRow(query string, args ...interface{}) pgx.Row {
	return db.pool.QueryRow(context.Background(), query, args...)
}
