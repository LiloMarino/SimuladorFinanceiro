from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from backend.types import JSONValue


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseDTO:
    def to_json(self) -> dict[str, JSONValue]:
        def convert(value):
            # Tipos primitivos — ok
            if value is None or isinstance(value, (str, int, float, bool)):
                return value

            # date / datetime → ISO 8601
            if isinstance(value, (date, datetime)):
                return value.isoformat()

            # Enum → value (string)
            if isinstance(value, Enum):
                return value.value

            # Decimal → float
            if isinstance(value, Decimal):
                return float(value)

            # DTO interno
            if isinstance(value, BaseDTO):
                return value.to_json()

            # Lista recursiva
            if isinstance(value, list):
                return [convert(v) for v in value]

            # Dict recursivo
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}

            # Dataclass genérico
            if is_dataclass(value):
                return {f.name: convert(getattr(value, f.name)) for f in fields(value)}

            # Última tentativa → string
            return str(value)

        return {f.name: convert(getattr(self, f.name)) for f in fields(self)}
