package containers

import (
	"fmt"
	"log"
	"quiniela-iac/internal/input"

	"aws_lib/aws_lib"

	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/ecr"
	"github.com/pulumi/pulumi-docker-build/sdk/go/dockerbuild"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

type Image struct {
	name        string
	repository  *ecr.Repository
	ctx         *pulumi.Context
	imgCfg      input.ImgCfg
	ImgResource *dockerbuild.Image
}

func NewImage(ctx *pulumi.Context, name string, imgCfg input.ImgCfg, repository *ecr.Repository) *Image {
	return &Image{
		name:       name,
		repository: repository,
		ctx:        ctx,
		imgCfg:     imgCfg,
	}
}

func (img *Image) PushImage(version string) pulumi.StringInput {
	authToken := img.authenticate()

	imageURI := img.repository.RepositoryUrl.ApplyT(func(repositoryUrl string) string {
		return fmt.Sprintf("%s:%s", repositoryUrl, version)
	}).(pulumi.StringInput)

	push := img.repository.RepositoryUrl.ApplyT(func(repositoryUrl string) bool {
		ecr := aws_lib.NewECR(input.GetRegion())
		push := !ecr.IsImageInECR(repositoryUrl, version)
		return push
	}).(pulumi.BoolInput)

	var err error
	img.ImgResource, err = dockerbuild.NewImage(
		img.ctx,
		fmt.Sprintf("%s-image", img.name),
		&dockerbuild.ImageArgs{
			Dockerfile: &dockerbuild.DockerfileArgs{
				Location: pulumi.Sprintf("../%s", img.imgCfg.Dockerfile),
			},
			Context: &dockerbuild.BuildContextArgs{
				Location: pulumi.Sprintf("../%s", img.imgCfg.Context),
			},
			Platforms: dockerbuild.PlatformArray{
				dockerbuild.Platform_Linux_amd64,
			},
			Registries: dockerbuild.RegistryArray{
				&dockerbuild.RegistryArgs{
					Address:  img.repository.RepositoryUrl,
					Password: authToken.Password(),
					Username: authToken.UserName(),
				},
			},
			Tags: pulumi.StringArray{imageURI},
			Push: push,
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	return imageURI
}

func (img *Image) authenticate() ecr.GetAuthorizationTokenResultOutput {
	return ecr.GetAuthorizationTokenOutput(
		img.ctx,
		ecr.GetAuthorizationTokenOutputArgs{
			RegistryId: img.repository.RegistryId,
		},
		nil,
	)
}
