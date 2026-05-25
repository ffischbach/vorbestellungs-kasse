from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Fischerfest Kassensystem"
    vereinsname: str = "ASG Ettlingen"
    event_jahr: int = 2026

    database_url: str = "sqlite:///./data/fischverkauf.db"

    printer_device: str = "/dev/usb/lp0"
    printer_enabled: bool = True

    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
