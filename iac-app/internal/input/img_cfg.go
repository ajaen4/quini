package input

type EnvVar struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

type ImgCfg struct {
	Dockerfile string `json:"dockerfile"`
	Context    string `json:"context"`
}

type SoleImgCfg struct {
	Dockerfile   string `json:"dockerfile"`
	Context      string `json:"context"`
	BuildVersion string `json:"build_version"`
}
