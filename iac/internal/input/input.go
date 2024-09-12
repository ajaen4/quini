package input

import (
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

type Input struct {
	Ctx          *pulumi.Context
	FunctionsCfg map[string]*FunctionCfg
}

type AWSCfg struct {
	Region string
}

var awsCfg AWSCfg

func Load(ctx *pulumi.Context) *Input {
	cfg := config.New(ctx, "")

	var funcsCfg map[string]*FunctionCfg
	if err := cfg.TryObject("functions", &funcsCfg); err != nil {
		funcsCfg = map[string]*FunctionCfg{}
	}

	aws := config.New(ctx, "aws")
	awsCfg = AWSCfg{
		Region: aws.Require("region"),
	}

	return &Input{
		Ctx:          ctx,
		FunctionsCfg: funcsCfg,
	}
}

func GetRegion() string {
	return awsCfg.Region
}
