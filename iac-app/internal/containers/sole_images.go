package containers

import (
	"fmt"
	"iac-app/internal/input"
	"log"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func NewImages(cfg *input.Input) {
	for imgName, imgCfg := range cfg.ImgsCfg {
		NewImg(cfg.Ctx, imgName, cfg.Env, imgCfg)
	}
}

func NewImg(ctx *pulumi.Context, name string, env string, soleImgCfg *input.SoleImgCfg) {
	quiniSeed, err := pulumi.NewStackReference(
		ctx,
		fmt.Sprintf("%s-stack-ref", name),
		&pulumi.StackReferenceArgs{
			Name: pulumi.String("ajaen4/quini-seed/main"),
		},
		nil,
	)
	if err != nil {
		log.Fatal(err)
	}

	repoUrl := quiniSeed.GetStringOutput(pulumi.Sprintf("%s-repo-url", name))
	registryId := quiniSeed.GetStringOutput(pulumi.Sprintf("%s-repo-registry-id", name))

	image := NewImage(
		ctx,
		name,
		input.ImgCfg{
			Dockerfile: soleImgCfg.Dockerfile,
			Context:    soleImgCfg.Context,
		},
		repoUrl,
		registryId,
	)
	image.PushImage(soleImgCfg.BuildVersion)
}
