from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configura o Pydantic para ler as variáveis de um arquivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Define as variáveis que sua aplicação espera.
    # O Pydantic irá validar se elas existem e se têm o tipo correto.
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Cria uma instância única que será importada em outros arquivos
settings = Settings()