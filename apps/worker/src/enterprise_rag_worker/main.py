from enterprise_rag_core.settings import get_settings


def main() -> None:
    settings = get_settings()
    print(
        f"worker placeholder started for {settings.environment} "
        f"using redis={settings.redis_dsn!s}"
    )

