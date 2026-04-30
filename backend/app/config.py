from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "FDE Enterprise Automation API"
    API_TOKEN: str = "change-this-token"
    CLUSTER_ID: str = "prod-ha-cluster-01"
    EXECUTION_MODE: str = "ssh"

    BASTION_HOST: str = "192.168.0.85"
    BASTION_PORT: int = 22
    BASTION_USER: str = "ubuntu"
    BASTION_KEY_PATH: str = "/opt/fde/keys/bastion.pem"

    KUBECONFIG_PATH: str = "/home/ubuntu/.kube/config"
    SSH_TIMEOUT: int = 10
    COMMAND_TIMEOUT: int = 30
    AUDIT_LOG_PATH: str = "./audit.log"
    CORS_ORIGINS: str = "*"


settings = Settings()
