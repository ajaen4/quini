package containers

import (
	"encoding/json"
	"fmt"
	"log"
	"quiniela-iac/internal/input"

	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/cloudwatch"
	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/ecs"
	"github.com/pulumi/pulumi-aws/sdk/v6/go/aws/iam"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

type task struct {
	ctx              *pulumi.Context
	name             string
	cfg              *input.TaskCfg
	publicSubnetsOut pulumi.AnyOutput
	sgId             pulumi.StringOutput
	roles            map[string]*iam.Role
}

func NewTask(ctx *pulumi.Context, name string, taskCfg *input.TaskCfg, roles map[string]*iam.Role) {
	baselineNetRef, err := pulumi.NewStackReference(ctx, "ajaen4/sityex-baseline/main", nil)
	if err != nil {
		log.Fatal(err)
	}
	task := &task{
		ctx:              ctx,
		name:             name,
		cfg:              taskCfg,
		publicSubnetsOut: baselineNetRef.GetOutput(pulumi.String("public_subnet_ids")),
		sgId:             baselineNetRef.GetOutput(pulumi.String("security_group_id")).AsStringOutput(),
		roles:            roles,
	}
	task.createECSTask()
}

func (task *task) createECSTask() {
	ecrRepo := NewRepository(
		task.ctx,
		task.name,
	)
	image := NewImage(
		task.ctx,
		task.name,
		task.cfg.ImgCfg,
		ecrRepo.EcrRepository,
	)
	imageURI := image.PushImage(task.cfg.BuildVersion)

	logGroup, err := cloudwatch.NewLogGroup(
		task.ctx,
		fmt.Sprintf("%s-log-group", task.name),
		&cloudwatch.LogGroupArgs{
			Name:            pulumi.String(fmt.Sprintf("/aws/ecs/task/%s", task.name)),
			RetentionInDays: pulumi.Int(30),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	clusterName := fmt.Sprintf("%s-cluster", task.name)
	cluster, err := ecs.NewCluster(
		task.ctx,
		clusterName,
		&ecs.ClusterArgs{
			Name: pulumi.String(clusterName),
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	envVars, err := json.Marshal(task.getEnvVars())
	if err != nil {
		log.Fatal(err)
	}

	containerDef := pulumi.All(imageURI, logGroup.Name).ApplyT(
		func(args []any) pulumi.StringOutput {
			return pulumi.Sprintf(`[
				{
					"name": "%s",
					"image": "%s",
					"essential": true,
					"logConfiguration": {
						"logDriver": "awslogs",
						"options": {
							"awslogs-group": "%s",
							"awslogs-region": "%s",
							"awslogs-stream-prefix": "%s-log-stream"
						}
					},
					"environment": %s
				}
			]`,
				task.name,
				args[0],
				args[1],
				input.GetRegion(),
				task.name,
				envVars,
			)
		},
	).(pulumi.StringOutput)

	taskDefName := fmt.Sprintf("%s-task-def", task.name)
	taskDef, err := ecs.NewTaskDefinition(
		task.ctx,
		taskDefName,
		&ecs.TaskDefinitionArgs{
			Family:                  pulumi.String(taskDefName),
			NetworkMode:             pulumi.String("awsvpc"),
			ContainerDefinitions:    containerDef,
			RequiresCompatibilities: pulumi.StringArray{pulumi.String("FARGATE")},
			Cpu:                     pulumi.Sprintf("%d", task.cfg.Cpu),
			Memory:                  pulumi.Sprintf("%d", task.cfg.Memory),
			ExecutionRoleArn:        task.roles["exec_role"].Arn,
			TaskRoleArn:             task.roles["task_role"].Arn,
		},
		pulumi.DependsOn([]pulumi.Resource{image.ImgResource}),
	)
	if err != nil {
		log.Fatal(taskDef)
	}

	if task.cfg.CronExpression != "" {
		task.createCronRule(cluster, taskDef)
	}
}

func (task *task) createCronRule(cluster *ecs.Cluster, taskDef *ecs.TaskDefinition) {
	ruleName := fmt.Sprintf("%s-schedule-rule", task.name)
	rule, err := cloudwatch.NewEventRule(
		task.ctx,
		ruleName,
		&cloudwatch.EventRuleArgs{
			Name:               pulumi.String(ruleName),
			ScheduleExpression: pulumi.String(task.cfg.CronExpression),
		})
	if err != nil {
		log.Fatal(err)
	}

	roleName := fmt.Sprintf("%s-cw-role", task.name)
	cwRole, err := iam.NewRole(
		task.ctx,
		roleName,
		&iam.RoleArgs{
			AssumeRolePolicy: pulumi.String(`{
			"Version": "2012-10-17",
			"Statement": [{
				"Effect": "Allow",
				"Principal": {
					"Service": "events.amazonaws.com"
				},
				"Action": "sts:AssumeRole"
			}]
		}`),
		})
	if err != nil {
		log.Fatal(err)
	}

	_, err = iam.NewRolePolicy(
		task.ctx,
		fmt.Sprintf("%s-cw-policy", task.name),
		&iam.RolePolicyArgs{
			Role: cwRole.Name,
			Policy: pulumi.String(`{
			"Version": "2012-10-17",
			"Statement": [{
				"Effect": "Allow",
				"Action": "ecs:RunTask",
				"Resource": "*"
			},{
				"Effect": "Allow",
				"Action": "iam:PassRole",
				"Resource": "*"
			}]
		}`),
		})
	if err != nil {
		log.Fatal(err)
	}

	_, err = cloudwatch.NewEventTarget(
		task.ctx,
		fmt.Sprintf("%s-event-target", task.name),
		&cloudwatch.EventTargetArgs{
			Rule:    rule.Name,
			Arn:     cluster.Arn,
			RoleArn: cwRole.Arn,
			EcsTarget: &cloudwatch.EventTargetEcsTargetArgs{
				TaskDefinitionArn: taskDef.Arn,
				NetworkConfiguration: &cloudwatch.EventTargetEcsTargetNetworkConfigurationArgs{
					Subnets:        pulumi.StringArray{pulumi.String("subnet-057777e539c1f3bb9"), pulumi.String("subnet-0bb462bb7beb560f9}")},
					SecurityGroups: pulumi.StringArray{pulumi.String("sg-0a36b4ca9b546d03d")},
					AssignPublicIp: pulumi.Bool(true),
				},
				LaunchType: pulumi.String("FARGATE"),
			},
		})
	if err != nil {
		log.Fatal(err)
	}
}

func (task *task) getEnvVars() []map[string]string {
	var envs []map[string]string
	for _, env := range task.cfg.EnvVars {
		envs = append(envs, map[string]string{
			"name":  env.Name,
			"value": env.Value,
		})
	}
	return envs
}
