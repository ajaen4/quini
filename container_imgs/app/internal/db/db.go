package db

import (
	"aws_lib/aws_lib"
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"sync"
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
	once       sync.Once
)

func New() Service {
	once.Do(func() {
		dbInstance = initDB()
	})
	return dbInstance
}

func initDB() *db {
	var sslmode string

	if env != "LOCAL" {
		sslmode = "require"
		sm := aws_lib.NewSSM("")
		param := sm.GetParam(fmt.Sprintf("/quini/secrets/%s", env), true)
		for varName, varValue := range param {
			if err := os.Setenv(varName, varValue); err != nil {
				log.Fatal("failed to set environment variable %s: %w", varName, err)
			}
		}
	}

	db_name := os.Getenv("DB_NAME")
	password := os.Getenv("DB_PASSWORD")
	username := os.Getenv("DB_USERNAME")
	port := os.Getenv("DB_PORT")
	host := os.Getenv("DB_HOST")

	connStr := fmt.Sprintf(
		"postgresql://%s:%s@%s:%s/%s?sslmode=%s",
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

	config.MinConns = 1
	config.ConnConfig.ConnectTimeout = 10 * time.Second
	if env == "LOCAL" {
		config.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol
	}

	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		log.Fatalf("Unable to create connection pool: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	if err := pool.Ping(ctx); err != nil {
		log.Fatalf("Unable to ping database: %v", err)
	}

	stats := pool.Stat()
	log.Printf("Initial pool stats - Total: %d, Acquired: %d, Idle: %d",
		stats.TotalConns(), stats.AcquiredConns(), stats.IdleConns())

	return &db{
		pool:     pool,
		db_name:  db_name,
		password: password,
		username: username,
		port:     port,
		host:     host,
	}
}

func (db *db) Health() map[string]string {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
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
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)

	stats := db.pool.Stat()
	log.Printf(
		"Pool stats before query - Total: %d, Acquired: %d, Idle: %d",
		stats.TotalConns(), stats.AcquiredConns(), stats.IdleConns(),
	)

	defer cancel()
	return db.pool.Query(ctx, query, args...)
}

func (db *db) QueryRow(query string, args ...interface{}) pgx.Row {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	stats := db.pool.Stat()
	log.Printf(
		"Pool stats before query - Total: %d, Acquired: %d, Idle: %d",
		stats.TotalConns(), stats.AcquiredConns(), stats.IdleConns(),
	)

	return db.pool.QueryRow(ctx, query, args...)
}
