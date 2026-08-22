"""Configuracion de la aplicacion, leida del entorno o del archivo .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno de la aplicacion.

    Pydantic busca cada campo primero en las variables de entorno del sistema
    y despues en el archivo .env. Si no lo encuentra, usa el valor por defecto.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Token opcional: sin el, GitHub permite 60 peticiones/hora por IP.
    github_token: str | None = None

    # Segundos que se reutiliza un analisis ya calculado. Con 0 se desactiva.
    cache_ttl_seconds: int = 300


# Instancia unica, importada por el resto de la aplicacion.
settings = Settings()
