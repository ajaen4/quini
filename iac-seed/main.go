package main

import (
	"fmt"
	"iac-seed/internal/containers"
	"iac-seed/internal/input"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		cfg := input.Load(ctx)

		for _, repoName := range cfg.Repos {
			repo := containers.NewRepository(ctx, repoName)

			ctx.Export(fmt.Sprintf("%s-repo-url", repoName), repo.RepositoryUrl)
			ctx.Export(fmt.Sprintf("%s-repo-registry-id", repoName), repo.RegistryId)
		}

		return nil
	})
}
