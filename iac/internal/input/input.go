package input

import (
	"fmt"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

type Input struct {
	Ctx      *pulumi.Context
	TasksCfg map[string]*TaskCfg
}

type AWSCfg struct {
	Region string
}

var awsCfg AWSCfg

func Load(ctx *pulumi.Context) *Input {
	cfg := config.New(ctx, "")

	var tasksCfg map[string]*TaskCfg
	if err := cfg.TryObject("tasks", &tasksCfg); err != nil {
		fmt.Print(err)
		tasksCfg = map[string]*TaskCfg{}
	}

	aws := config.New(ctx, "aws")
	awsCfg = AWSCfg{
		Region: aws.Require("region"),
	}

	return &Input{
		Ctx:      ctx,
		TasksCfg: tasksCfg,
	}
}

func GetRegion() string {
	return awsCfg.Region
}
