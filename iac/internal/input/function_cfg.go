package input

type FunctionCfg struct {
	ImgCfg         ImgCfg   `json:"image"`
	BuildVersion   string   `json:"build_version"`
	EnvVars        []EnvVar `json:"env_vars"`
	CronExpression string   `json:"cron_expression"`
}
