from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
        # A resposta sempre traz todos os campos: o schema de saída os marca como obrigatórios
        json_schema_serialization_defaults_required=True,
    )

    def to_json(self):
        return self.model_dump(mode="json")
