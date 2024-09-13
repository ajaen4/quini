package main

import (
	"bavariada-iac/internal/containers"
	"bavariada-iac/internal/input"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		cfg := input.Load(ctx)

		containers.NewFunctions(cfg)

		return nil
	})
}
