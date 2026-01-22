import asyncio
from typing import ClassVar

from backend import config
from backend.core.dto.tunnel_status import TunnelStatus
from backend.core.logger import setup_logger
from backend.features.tunnel.providers import AVAILABLE_PROVIDERS
from backend.features.tunnel.providers.lan_provider import LANProvider
from backend.features.tunnel.tunnel_provider import TunnelProvider

logger = setup_logger(__name__)


class TunnelManager:
    """
    Gerenciador singleton de túneis de rede.

    Responsável por:
    - Instanciar o provider correto baseado na configuração TOML
    - Gerenciar lifecycle do túnel (start/stop)
    - Emitir eventos realtime para clientes conectados
    - Fornecer status do túnel
    """

    _config = config.toml.server
    _provider: TunnelProvider = AVAILABLE_PROVIDERS[_config.provider]()
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def start_tunnel(cls) -> TunnelStatus:
        """
        Inicia o túnel usando o provider configurado.
        """
        async with cls._lock:
            if cls._config.provider == "lan":
                raise ValueError(
                    "Provider LAN não suporta essa operação. "
                    "Configure um provider ativo em config.toml "
                )

            if cls._provider.is_active():
                return TunnelStatus(
                    active=True,
                    url=cls._provider.get_public_url(),
                    provider=cls._provider.name,
                )

            url = await cls._provider.start(cls._config.port)
            return TunnelStatus(active=True, url=url, provider=cls._provider.name)

    @classmethod
    async def stop_tunnel(cls):
        """
        Para o túnel ativo.
        """
        async with cls._lock:
            if cls._config.provider == "lan":
                raise ValueError(
                    "Provider LAN não suporta essa operação. "
                    "Configure um provider ativo em config.toml "
                )

            if not cls._provider.is_active():
                raise ValueError("Nenhum túnel ativo para parar")

            await cls._provider.stop()

    @classmethod
    def get_status(cls) -> TunnelStatus:
        """
        Retorna status atual do túnel.
        """
        # Garante que provider LAN está inicializado para detectar IPs
        if isinstance(cls._provider, LANProvider):
            cls._provider._initialize_ips()
            cls._provider._port = cls._config.port
            cls._provider._initialized = True

        return TunnelStatus(
            active=cls._provider.is_active(),
            url=cls._provider.get_public_url(),
            provider=cls._provider.name,
        )

    @classmethod
    def get_public_url(cls) -> str | None:
        """Retorna apenas a URL pública se túnel estiver ativo."""
        return cls._provider.get_public_url()
