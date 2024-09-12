package containers

import (
	"log"

	"quiniela-iac/internal/input"
	"quiniela-iac/internal/types"

	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/iam"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func NewTasks(cfg *input.Input) {
	roles := createRoles(cfg.Ctx)
	for taskName, taskCfg := range cfg.TasksCfg {
		NewTask(cfg.Ctx, taskName, taskCfg, roles)
	}
}

func createRoles(ctx *pulumi.Context) map[string]*iam.Role {
	assumeRPol := types.ValidateJSON(`{
		"Version": "2008-10-17",
		"Statement": [
			{
				"Action": "sts:AssumeRole",
				"Principal": {"Service": "ecs-tasks.amazonaws.com"},
				"Effect": "Allow"
			}
		]
	}`)

	execPol := types.ValidateJSON(`{
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Action": [
					"ecs:StartTask",
					"ecs:StopTask",
					"ecs:DescribeTasks",
					"ecr:GetAuthorizationToken",
					"ecr:BatchCheckLayerAvailability",
					"ecr:GetDownloadUrlForLayer",
					"ecr:BatchGetImage",
					"logs:CreateLogStream",
					"logs:PutLogEvents",
					"elasticfilesystem:ClientMount",
					"elasticfilesystem:ClientWrite",
					"elasticfilesystem:ClientRootAccess",
					"elasticfilesystem:DescribeFileSystems"
				],
				"Resource": "*"
			}
		]
	}`)

	taskPolicy := types.ValidateJSON(`{
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Action": [
					"elasticloadbalancing:Describe*",
					"elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
					"elasticloadbalancing:RegisterInstancesWithLoadBalancer",
					"ec2:Describe*",
					"ec2:AuthorizeSecurityGroupIngress",
					"elasticloadbalancing:RegisterTargets",
					"elasticloadbalancing:DeregisterTargets",
					"elasticfilesystem:ClientMount",
					"elasticfilesystem:ClientWrite",
					"elasticfilesystem:ClientRootAccess",
					"elasticfilesystem:DescribeFileSystems",
					"ssm:*"
				],
				"Resource": "*"
			}
		]
	}`)

	execRoleName := "quiniela-task-exec-role"
	execRole, err := iam.NewRole(
		ctx,
		execRoleName,
		&iam.RoleArgs{
			Name:             pulumi.String(execRoleName),
			AssumeRolePolicy: pulumi.String(assumeRPol),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	execPolName := "quiniela-task-exec-policy"
	_, err = iam.NewRolePolicy(
		ctx,
		execPolName,
		&iam.RolePolicyArgs{
			Name:   pulumi.String(execPolName),
			Role:   execRole.ID(),
			Policy: pulumi.String(execPol),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	taskRoleName := "quiniela-task-role"
	taskRole, err := iam.NewRole(
		ctx,
		taskRoleName,
		&iam.RoleArgs{
			Name:             pulumi.String(taskRoleName),
			AssumeRolePolicy: pulumi.String(assumeRPol),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	taskPolicyName := "quiniela-task-policy"
	_, err = iam.NewRolePolicy(
		ctx,
		taskPolicyName,
		&iam.RolePolicyArgs{
			Name:   pulumi.String(taskPolicyName),
			Role:   taskRole.ID(),
			Policy: pulumi.String(taskPolicy),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	return map[string]*iam.Role{
		"exec_role": execRole,
		"task_role": taskRole,
	}
}
