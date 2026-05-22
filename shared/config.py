from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_backend: str = "deepseek_api"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "chuanyu_finance"
    postgres_user: str = "chuanyu"
    postgres_password: str = "chuanyu_dev_pwd"

    # Crawler
    crawl_interval_hours: int = 24
    crawl_trading_day_only: bool = True

    # Scheduler
    schedule_time: str = "16:00"
    news_retention_days: int = 30
    policy_retention_days: int = 365

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
