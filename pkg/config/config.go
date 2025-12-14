package config

import (
	"os"

	"github.com/makeok/go-web-init/pkg/utils/ratelimit"

	"gopkg.in/yaml.v2"
)

type Config struct {
	Server      ServerConfig           `yaml:"server"`
	Postgres    DBConfig               `yaml:"postgres"`
	Mysql       DBConfig               `yaml:"mysql"`
	Sqlite      DBConfig               `yaml:"sqlite"`
	Redis       RedisConfig            `yaml:"redis"`
	OAuthConfig map[string]OAuthConfig `yaml:"oauth"`
	Docker      DockerConfig           `yaml:"docker"`
	Kubernetes  KubeConfig             `yaml:"kubernetes"`
}

type ServerConfig struct {
	ENV                    string                  `yaml:"env"`
	Address                string                  `yaml:"address"`
	Port                   int                     `yaml:"port"`
	GracefulShutdownPeriod int                     `yaml:"gracefulShutdownPeriod"`
	LimitConfigs           []ratelimit.LimitConfig `yaml:"rateLimits"`
	JWTSecret              string                  `yaml:"jwtSecret"`
	DbType                 string                  `yaml:"dbType"`
}

type DBConfig struct {
	Host     string `yaml:"host"`
	Port     int    `yaml:"port"`
	Name     string `yaml:"name"`
	User     string `yaml:"user"`
	Password string `yaml:"password"`
	Migrate  bool   `yaml:"migrate"`
	File     string `yaml:"file"`
}

type RedisConfig struct {
	Enable   bool   `yaml:"enable"`
	Host     string `yaml:"host"`
	Port     int    `yaml:"port"`
	Password string `yaml:"password"`
}

type OAuthConfig struct {
	AuthType     string `yaml:"authType"`
	ClientId     string `yaml:"clientId"`
	ClientSecret string `yaml:"clientSecret"`
}

type DockerConfig struct {
	Enable bool   `yaml:"enable"`
	Host   string `yaml:"host"`
}

type KubeConfig struct {
	Enable         bool     `yaml:"enable"`
	WatchResources []string `yaml:"watchResources"`
}

func Parse(appConfig string) (*Config, error) {
	config := &Config{}

	file, err := os.Open(appConfig)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	if err := yaml.NewDecoder(file).Decode(&config); err != nil {
		return nil, err
	}

	return config, nil
}
