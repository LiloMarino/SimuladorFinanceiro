from backend.features.tunnel.network_utils.network_interface import NetworkInterface
from backend.features.tunnel.network_utils.network_types import NetworkType


class NetworkPolicy:
    DEFAULT_PRIORITY: tuple[NetworkType, ...] = (
        NetworkType.RADMIN,
        NetworkType.HAMACHI,
        NetworkType.TAILSCALE,
        NetworkType.LAN,
    )

    def select(
        self,
        interfaces: list[NetworkInterface],
        preferred: NetworkType | None = None,
    ) -> NetworkInterface | None:
        if not interfaces:
            return None

        if preferred:
            for interface in interfaces:
                if interface.kind == preferred:
                    return interface

        for kind in self.DEFAULT_PRIORITY:
            for interface in interfaces:
                if interface.kind == kind:
                    return interface

        return None
