from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    NOTICE_CRAWL_HOUR: int = 18
    NOTICE_CRAWL_MINUTE: int = 0
    SOOKMYUNG_NOTICE_URL: str = (
        "https://www.sookmyung.ac.kr/kr/university-life/nformation07-popup.do"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
