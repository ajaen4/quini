package input

import (
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

type Input struct {
	Ctx          *pulumi.Context
	FunctionsCfg map[string]*FunctionCfg
	ImgsCfg      map[string]*SoleImgCfg
	Env          string
}

type AWSCfg struct {
	Region string
}

var awsCfg AWSCfg

func Load(ctx *pulumi.Context) *Input {
	cfg := config.New(ctx, "")

	env := cfg.Require("env")

	var funcsCfg map[string]*FunctionCfg
	if err := cfg.TryObject("functions", &funcsCfg); err != nil {
		funcsCfg = map[string]*FunctionCfg{}
	}

	var imgsCfg map[string]*SoleImgCfg
	if err := cfg.TryObject("images", &imgsCfg); err != nil {
		imgsCfg = map[string]*SoleImgCfg{}
	}

	aws := config.New(ctx, "aws")
	awsCfg = AWSCfg{
		Region: aws.Require("region"),
	}

	return &Input{
		Ctx:          ctx,
		FunctionsCfg: funcsCfg,
		ImgsCfg:      imgsCfg,
		Env:          env,
	}
}

func GetRegion() string {
	return awsCfg.Region
}
