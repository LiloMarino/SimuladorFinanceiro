import asyncio
from typing import ClassVar

from backend import config
from backend.core.dto.tunnel_status import TunnelStatusDTO
from backend.core.logger import setup_logger
from backend.features.tunnel.providers import AVAILABLE_PROVIDERS
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
    _task: asyncio.Task | None = None

    @classmethod
    async def start_tunnel(cls) -> TunnelStatusDTO:
        async with cls._lock:
            if cls._provider.is_active():
                return TunnelStatusDTO(
                    active=True,
                    url=cls._provider.get_public_url(),
                    provider=cls._provider.name,
                )

            url = await cls._provider.start(cls._config.port)
            return TunnelStatusDTO(active=True, url=url, provider=cls._provider.name)

    @classmethod
    async def stop_tunnel(cls):
        async with cls._lock:
            if not cls._provider.is_active():
                raise ValueError("Nenhum túnel ativo para parar")

            await cls._provider.stop()

    @classmethod
    def get_status(cls) -> TunnelStatusDTO:
        return TunnelStatusDTO(
            active=cls._provider.is_active(),
            url=cls._provider.get_public_url(),
            provider=cls._provider.name,
        )

    @classmethod
    def get_public_url(cls) -> str | None:
        """Retorna apenas a URL pública se túnel estiver ativo."""
        return cls._provider.get_public_url()
