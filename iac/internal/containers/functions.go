package containers

import (
	"fmt"
	"log"
	"quiniela-iac/internal/input"

	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/cloudwatch"
	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/iam"
	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/lambda"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func NewFunctions(cfg *input.Input) {
	for funcName, funcCfg := range cfg.FunctionsCfg {
		NewFunction(cfg.Ctx, funcName, funcCfg)
	}
}

type function struct {
	ctx  *pulumi.Context
	name string
	cfg  *input.FunctionCfg
}

func NewFunction(ctx *pulumi.Context, name string, funcCfg *input.FunctionCfg) {
	function := &function{
		ctx:  ctx,
		name: name,
		cfg:  funcCfg,
	}
	function.deploy()
}

func (function *function) deploy() {
	role := function.createRole()
	function.createFunction(role)
}

func (function *function) createRole() *iam.Role {
	role, err := iam.NewRole(
		function.ctx,
		fmt.Sprintf("%s-role", function.name),
		&iam.RoleArgs{
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
		fmt.Sprintf("%s-policy", function.name),
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
		fmt.Sprintf("%s-ecr-policy", function.name),
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
		fmt.Sprintf("%s-ecr-policy-attch", function.name),
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
	repo := NewRepository(function.ctx, function.name)
	image := NewImage(
		function.ctx,
		function.name,
		function.cfg.ImgCfg,
		repo.EcrRepository,
	)
	imageUrl := image.PushImage(function.cfg.BuildVersion)

	lambdaFunction, err := lambda.NewFunction(
		function.ctx,
		fmt.Sprintf("%s-function", function.name),
		&lambda.FunctionArgs{
			Name:        pulumi.String(function.name),
			Role:        role.Arn,
			ImageUri:    imageUrl,
			PackageType: pulumi.String("Image"),
			Timeout:     pulumi.Int(900),
			Environment: &lambda.FunctionEnvironmentArgs{
				Variables: function.parseEnvs(),
			},
			VpcConfig: &lambda.FunctionVpcConfigArgs{
				SubnetIds: pulumi.ToStringArray([]string{
					"subnet-0c9b8ec96e8062d5e",
					"subnet-06705f7071627b8d8",
				}),
				SecurityGroupIds: pulumi.ToStringArray([]string{
					"sg-06a3a96570494b00f",
				}),
			},
		},
		pulumi.DependsOn([]pulumi.Resource{image.ImgResource}),
	)
	if err != nil {
		log.Fatal(err)
	}

	if function.cfg.CronExpression != "" {
		rule, err := cloudwatch.NewEventRule(
			function.ctx,
			fmt.Sprintf("%s-cron-rule", function.name),
			&cloudwatch.EventRuleArgs{
				Name:               pulumi.Sprintf("%s-cron-rule", function.name),
				Description:        pulumi.Sprintf("Cron trigger for %s-", function.name),
				ScheduleExpression: pulumi.String(function.cfg.CronExpression),
			})
		if err != nil {
			log.Fatal(err)
		}

		_, err = lambda.NewPermission(
			function.ctx,
			fmt.Sprintf("%s-cron-invoke", function.name),
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
			fmt.Sprintf("%s-cron-target", function.name),
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
