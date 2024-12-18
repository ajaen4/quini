package containers

import (
	"fmt"
	"iac-app/internal/input"
	"log"

	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/cloudwatch"
	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/iam"
	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/lambda"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func NewFunctions(cfg *input.Input) {
	for funcName, funcCfg := range cfg.FunctionsCfg {
		NewFunction(cfg.Ctx, funcName, cfg.Env, funcCfg)
	}
}

type function struct {
	ctx  *pulumi.Context
	name string
	env  string
	cfg  *input.FunctionCfg
}

func NewFunction(ctx *pulumi.Context, name string, env string, funcCfg *input.FunctionCfg) {
	function := &function{
		ctx:  ctx,
		name: name,
		env:  env,
		cfg:  funcCfg,
	}
	function.deploy()
}

func (function *function) deploy() {
	role := function.createRole()
	function.createFunction(role)
}

func (function *function) createRole() *iam.Role {
	roleName := fmt.Sprintf("%s-role-%s", function.name, function.env)
	role, err := iam.NewRole(
		function.ctx,
		roleName,
		&iam.RoleArgs{
			Name: pulumi.String(roleName),
			AssumeRolePolicy: pulumi.String(`{
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }]
        }`),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	_, err = iam.NewRolePolicyAttachment(
		function.ctx,
		fmt.Sprintf("%s-policy-%s", function.name, function.env),
		&iam.RolePolicyAttachmentArgs{
			Role: role.Name,
			PolicyArn: pulumi.String(
				"arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
			),
		})
	if err != nil {
		log.Fatal(err)
	}

	ecrPolicy, err := iam.NewPolicy(
		function.ctx,
		fmt.Sprintf("%s-ecr-policy-%s", function.name, function.env),
		&iam.PolicyArgs{
			Description: pulumi.String("IAM policy for Lambda to access ECR"),
			Policy: pulumi.String(`{
			"Version": "2012-10-17",
			"Statement": [
				{
					"Effect": "Allow",
					"Action": [
						"ecr:*",
						"ssm:*",
						"ec2:*"
					],
					"Resource": "*"
				}
			]
		}`),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	_, err = iam.NewRolePolicyAttachment(
		function.ctx,
		fmt.Sprintf("%s-ecr-policy-attch-%s", function.name, function.env),
		&iam.RolePolicyAttachmentArgs{
			Role:      role.Name,
			PolicyArn: ecrPolicy.Arn,
		})
	if err != nil {
		log.Fatal(err)
	}

	return role
}

func (function *function) createFunction(role *iam.Role) {
	quiniSeed, err := pulumi.NewStackReference(function.ctx, "ajaen4/quini-seed/main", nil)
	if err != nil {
		log.Fatal(err)
	}

	repoUrl := quiniSeed.GetStringOutput(pulumi.Sprintf("%s-repo-url", function.name))
	registryId := quiniSeed.GetStringOutput(pulumi.Sprintf("%s-repo-registry-id", function.name))
	funcName := fmt.Sprintf("%s-%s", function.name, function.env)

	image := NewImage(
		function.ctx,
		funcName,
		function.cfg.ImgCfg,
		repoUrl,
		registryId,
	)
	imageUrl := image.PushImage(function.cfg.BuildVersion)

	lambdaFunction, err := lambda.NewFunction(
		function.ctx,
		funcName,
		&lambda.FunctionArgs{
			Name:        pulumi.String(funcName),
			Role:        role.Arn,
			ImageUri:    imageUrl,
			PackageType: pulumi.String("Image"),
			Timeout:     pulumi.Int(900),
			Environment: &lambda.FunctionEnvironmentArgs{
				Variables: function.parseEnvs(),
			},
		},
		pulumi.DependsOn([]pulumi.Resource{image.ImgResource}),
	)
	if err != nil {
		log.Fatal(err)
	}

	if function.cfg.CronExpression != "" {
		eventRuleName := fmt.Sprintf("%s-cron-rule-%s", function.name, function.env)
		rule, err := cloudwatch.NewEventRule(
			function.ctx,
			eventRuleName,
			&cloudwatch.EventRuleArgs{
				Name:               pulumi.String(eventRuleName),
				Description:        pulumi.Sprintf("Cron trigger for %s-", function.name),
				ScheduleExpression: pulumi.String(function.cfg.CronExpression),
			})
		if err != nil {
			log.Fatal(err)
		}

		_, err = lambda.NewPermission(
			function.ctx,
			fmt.Sprintf("%s-cron-invoke-%s", function.name, function.env),
			&lambda.PermissionArgs{
				Action:    pulumi.String("lambda:InvokeFunction"),
				Function:  lambdaFunction.Name,
				Principal: pulumi.String("events.amazonaws.com"),
				SourceArn: rule.Arn,
			})
		if err != nil {
			log.Fatal(err)
		}

		_, err = cloudwatch.NewEventTarget(
			function.ctx,
			fmt.Sprintf("%s-cron-target-%s", function.name, function.env),
			&cloudwatch.EventTargetArgs{
				Rule: rule.Name,
				Arn:  lambdaFunction.Arn,
			})
		if err != nil {
			log.Fatal(err)
		}
	}
}

func (function *function) parseEnvs() pulumi.StringMapInput {
	var envs = pulumi.StringMap{}
	for _, env := range function.cfg.EnvVars {
		envs[env.Name] = pulumi.String(env.Value)
	}
	return envs
}
