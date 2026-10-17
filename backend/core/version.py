import tomllib
from functools import cache

from backend.core.utils import resource_path


@cache
def get_version() -> str:
    """Versão do app: o campo `version` do `pyproject.toml`, que vai junto no executável."""
    with resource_path("pyproject.toml").open("rb") as file:
        return tomllib.load(file)["project"]["version"]
