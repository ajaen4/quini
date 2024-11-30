package main

import (
	"iac-app/internal/containers"
	"iac-app/internal/input"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		cfg := input.Load(ctx)

		containers.NewFunctions(cfg)
		containers.NewImages(cfg)

		return nil
	})
}
