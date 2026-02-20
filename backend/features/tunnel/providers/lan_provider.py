import logging

from backend import config
from backend.features.tunnel.network_utils.network_detector import NetworkDetector
from backend.features.tunnel.network_utils.network_interface import NetworkInterface
from backend.features.tunnel.network_utils.network_policy import NetworkPolicy
from backend.features.tunnel.tunnel_provider import TunnelProvider

logger = logging.getLogger(__name__)


class LANProvider(TunnelProvider):
    """
    Provider de detecção de interfaces LAN e VPN locais.

    Responsável por:
    - Detectar interfaces de rede locais e VPNs (Radmin, Hamachi, Tailscale)
    - Selecionar melhor interface baseado em política de prioridade
    - Fornecer URL de acesso usando IP detectado + porta
    - Não criar túnel (apenas descoberta de rede)
    """

    def __init__(self):
        self._detector = NetworkDetector()
        self._policy = NetworkPolicy()
        self._preferred = config.toml.server.preferred_vpn
        self._show_firewall_hint = config.toml.server.show_firewall_hint
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

        if self._show_firewall_hint:
            self._log_firewall_hint(port)

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

    def _log_firewall_hint(self, port: int) -> None:
        logger.info(
            f"Para acesso externo, pode ser necessário permitir o aplicativo no firewall ou liberar a porta {port}."
        )
