import os
from pathlib import Path


def load_dotenv_if_present(path: Path | None = None) -> None:
    """
    Load .env file if python-dotenv is installed.
    Safe: no-op if dotenv is missing or file not found.
    """
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return

    env_path = path or Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
}

def get_api_key(provider: str, *, required: bool = True) -> str | None:
    env_var = PROVIDER_ENV_KEYS.get(provider)
    if not env_var:
        raise ValueError(f"Unknown provider: {provider}")

    key = os.getenv(env_var)

    if required and not key:
        raise RuntimeError(
            f"{env_var} is not set. "
            f"Export it as an environment variable or via .env"
        )

    return key