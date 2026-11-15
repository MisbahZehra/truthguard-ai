import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_environment() -> None:
    values = dotenv_values(ENV_PATH)
    for key, value in values.items():
        if value and key in os.environ and not os.environ[key].strip():
            os.environ[key] = value
    load_dotenv(ENV_PATH, override=False)


load_environment()


@dataclass
class Settings:
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    llm_base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", ""))
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", ""))
    api_keys: set = field(default_factory=lambda: {k for k in os.getenv("TRUTHGUARD_API_KEYS", "dev-key").split(",") if k})
    db_path: str = field(default_factory=lambda: os.getenv("DB_PATH", "truthguard.db"))
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL_SECONDS", "900")))
    rate_limit: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MIN", "30")))
    concurrency: int = field(default_factory=lambda: int(os.getenv("CONCURRENCY", "4")))

    ui_enabled: bool = field(default_factory=lambda: os.getenv("UI_ENABLED", "true").lower() == "true")
    retention_days: int = field(default_factory=lambda: int(os.getenv("RETENTION_DAYS", "30")))
    static_dir: str = field(default_factory=lambda: os.getenv("STATIC_DIR", ""))

    @property
    def live(self) -> bool:
        return bool(self.tavily_api_key)
