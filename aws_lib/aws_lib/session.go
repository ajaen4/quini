package aws_lib

import (
	"log"
	"sync"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
)

var (
	sess *session.Session
	once sync.Once
)

func GetSession(region string) *session.Session {
	once.Do(func() {
		var err error
		sess, err = session.NewSessionWithOptions(session.Options{
			SharedConfigState: session.SharedConfigEnable,
			Config: aws.Config{
				Region: aws.String(region),
			},
		})
		if err != nil {
			log.Fatalf("Failed to create AWS session: %v", err)
		}
	})
	return sess
}
