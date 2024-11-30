package containers

import (
	"fmt"
	"log"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"

	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/ecr"
)

type Repository struct {
	Ctx *pulumi.Context
}

func NewRepository(ctx *pulumi.Context, name string) *ecr.Repository {
	repository, err := ecr.NewRepository(
		ctx,
		fmt.Sprintf("%s-repository", name),
		&ecr.RepositoryArgs{
			Name:               pulumi.String(name),
			ImageTagMutability: pulumi.String("IMMUTABLE"),
			ImageScanningConfiguration: &ecr.RepositoryImageScanningConfigurationArgs{
				ScanOnPush: pulumi.Bool(true),
			},
			ForceDelete: pulumi.Bool(true),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	_, err = ecr.NewRepositoryPolicy(
		ctx,
		fmt.Sprintf("%s-repository-policy", name),
		&ecr.RepositoryPolicyArgs{
			Repository: repository.Name,
			Policy: pulumi.String(`{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowPublicPull",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "ecr:GetDownloadUrlForLayer",
                            "ecr:BatchGetImage",
                            "ecr:BatchCheckLayerAvailability"
                        ]
                    }
                ]
            }`),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	return repository
}
