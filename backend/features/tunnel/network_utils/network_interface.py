from dataclasses import dataclass

from backend.features.tunnel.network_utils.network_types import NetworkType


@dataclass(frozen=True, slots=True, kw_only=True)
class NetworkInterface:
    ip: str
    kind: NetworkType

    @property
    def name(self) -> str:
        return self.kind.display_name

    @property
    def icon(self) -> str:
        return self.kind.icon
