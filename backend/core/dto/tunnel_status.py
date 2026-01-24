from backend.core.dto.base import BaseDTO


class TunnelStatusDTO(BaseDTO):
    active: bool
    url: str | None
    provider: str | None
