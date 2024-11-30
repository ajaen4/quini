package input

import (
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

type Input struct {
	Ctx   *pulumi.Context
	Repos []string
}

type AWSCfg struct {
	Region string
}

var awsCfg AWSCfg

func Load(ctx *pulumi.Context) *Input {
	cfg := config.New(ctx, "")

	var repos []string
	cfg.RequireObject("repos", &repos)
	aws := config.New(ctx, "aws")
	awsCfg = AWSCfg{
		Region: aws.Require("region"),
	}

	return &Input{
		Ctx:   ctx,
		Repos: repos,
	}
}

func GetRegion() string {
	return awsCfg.Region
}
