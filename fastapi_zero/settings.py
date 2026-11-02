# Importa BaseSettings para trabalhar com variáveis de ambiente.
# SettingsConfigDict permite configurar o comportamento do BaseSettings.
from pydantic_settings import BaseSettings, SettingsConfigDict


# Classe responsável por centralizar as configurações do projeto.
class Settings(BaseSettings):
    # Configura o Pydantic para procurar as variáveis
    # de ambiente no arquivo .env.
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    # Define uma variável obrigatória.
    # Seu valor será carregado do arquivo .env.
    DATABASE_URL: str
