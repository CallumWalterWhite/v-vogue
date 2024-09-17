import secrets
from typing import Annotated, Any, Literal, Optional

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.ENVIRONMENT == "local":
            # Use SQLite for local development
            return f"sqlite:///./{self.LOCAL_DB}"
        else:
            # Use PostgreSQL for staging/production
            return MultiHostUrl.build(
                scheme="postgresql+psycopg2",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"/{self.POSTGRES_DB}",
            )

    PROJECT_NAME: str = "FastAPI app"
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    LOCAL_DB: str = "local.db"
     
    LOAD_VITONHD_MODEL: bool = True
    LOAD_CLOTH_SEGMENTATION_MODEL: bool = True
    LOAD_OPEN_POSE_MODEL: bool = True
    LOAD_HUMAN_PARSING_MODEL: bool = True
    LOAD_DENPOSE_MODEL: bool = True
    VITONHD_MODEL_CONFIG_PATH: str = "../vitonhd/configs/VITONHD.yaml"
    VITONHD_MODEL_PATH: str = "../vitonhd/VITONHD.ckpt"
    CLOTH_SEGMENTATION_MODEL_PATH: str = "../cloth_segmentation/trained_checkpoint/checkpoint_u2net.pth"
    
    STORAGE_SETTING: Literal["local", "azure"] = "local"
    
    IS_LOCAL_MESSAGING: bool = True
    INBOX_INTERNAL_REQUEST_URL: str = "http://127.0.0.1:8000/api/v1/message/inbox"

settings = Settings()  # type: ignore