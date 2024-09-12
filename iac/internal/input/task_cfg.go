package input

type TaskCfg struct {
	BuildVersion   string   `json:"build_version"`
	ImgCfg         ImgCfg   `json:"image"`
	Cpu            int      `json:"cpu"`
	Memory         int      `json:"memory"`
	EnvVars        []EnvVar `json:"env_vars"`
	CronExpression string   `json:"cron_expression"`
}
