from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    port: int = 8000
    def log_level(self):
        return "debug" if self.env == "local" else "error"

def configure() -> Settings:
    return Settings()