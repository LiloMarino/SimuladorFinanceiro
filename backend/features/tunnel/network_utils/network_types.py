from enum import Enum


class NetworkType(str, Enum):
    RADMIN = "radmin"
    HAMACHI = "hamachi"
    TAILSCALE = "tailscale"
    LAN = "lan"

    @property
    def display_name(self) -> str:
        return {
            NetworkType.RADMIN: "Radmin VPN",
            NetworkType.HAMACHI: "LogMeIn Hamachi",
            NetworkType.TAILSCALE: "Tailscale",
            NetworkType.LAN: "LAN Local",
        }[self]

    @property
    def icon(self) -> str:
        return {
            NetworkType.RADMIN: "📡",
            NetworkType.HAMACHI: "🔗",
            NetworkType.TAILSCALE: "🛰️",
            NetworkType.LAN: "🏠",
        }[self]
