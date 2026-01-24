from backend import config
from backend.core.logger import setup_logger
from backend.features.tunnel.network_utils.network_detector import NetworkDetector
from backend.features.tunnel.network_utils.network_interface import NetworkInterface
from backend.features.tunnel.network_utils.network_policy import NetworkPolicy
from backend.features.tunnel.tunnel_provider import TunnelProvider

logger = setup_logger(__name__)


class LANProvider(TunnelProvider):
    """
    Provider LAN:
    - Não cria túnel
    - Não inicia subprocessos
    - Apenas detecta interfaces locais/VPNs e escolhe a melhor
    """

    def __init__(self):
        self._detector = NetworkDetector()
        self._policy = NetworkPolicy()
        self._preferred = config.toml.server.preferred_vpn
        self._interfaces: list[NetworkInterface] = []
        self._active = False
        self._port: int | None = None

    @property
    def name(self) -> str:
        return "lan"

    async def start(self, port: int) -> str:
        self._port = port
        self._interfaces = self._detector.detect()

        if not self._interfaces:
            logger.warning(
                "⚠️ Nenhuma interface LAN/VPN detectada. "
                "Ative Radmin/Hamachi ou conecte-se a uma rede local."
            )
            self._active = False
            return ""

        self._active = True

        logger.info(f"🌐 Interfaces detectadas (porta {port}):")
        for interface in self._interfaces:
            logger.info(
                f"  {interface.icon} [{interface.name}] http://{interface.ip}:{port}"
            )

        self._log_firewall_warning(port)

        best = self._policy.select(self._interfaces, self._preferred)
        return self._url_for(best) if best else ""

    async def stop(self) -> None:
        raise NotImplementedError(
            "Provider LAN não suporta essa operação. "
            "Configure um provider ativo em config.toml "
        )

    def is_active(self) -> bool:
        return self._active and bool(self._interfaces)

    def get_public_url(self) -> str | None:
        if not self.is_active():
            return None

        best = self._policy.select(self._interfaces, self._preferred)
        return self._url_for(best) if best else None

    def get_all_urls(self) -> list[dict]:
        if not self.is_active():
            return []

        return [
            {
                "ip": interface.ip,
                "url": self._url_for(interface),
                "type": interface.kind.value,
                "name": interface.name,
                "icon": interface.icon,
            }
            for interface in self._interfaces
        ]

    # =========================
    # Helpers
    # =========================

    def _url_for(self, interface: NetworkInterface | None) -> str:
        if not interface or not self._port:
            return ""
        return f"http://{interface.ip}:{self._port}"

    def _log_firewall_warning(self, port: int) -> None:
        logger.warning(
            f"Para aceitar conexões externas, abra a porta {port} no firewall:"
        )
        logger.warning("   Windows: Settings > Privacy & Security > Firewall")
        logger.warning(f"   Linux: sudo ufw allow {port}/tcp")
        logger.warning("   macOS: System Settings > Network > Firewall")
