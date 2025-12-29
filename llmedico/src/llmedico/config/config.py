import logging

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.10 and below

from pathlib import Path
logger = logging.getLogger(__name__)

class Config:
    def __init__(self, path: Path | None = None):
        self.path = path or Path("config.toml")

        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")

        with self.path.open("rb") as f:
            self._data = tomllib.load(f)

        logger.debug(f"Loaded config from {self.path}")

    def section(self, name: str) -> dict:
        return self._data.get(name, {})

    def get(self, section: str, key: str, default=None):
        return self._data.get(section, {}).get(key, default)

    def __repr__(self):
        return f"<Config path={self.path}>"
