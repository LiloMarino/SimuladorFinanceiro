from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
        json_encoders={
            Decimal: float,
        },
    )

    def to_json(self):
        return self.model_dump(mode="json")
