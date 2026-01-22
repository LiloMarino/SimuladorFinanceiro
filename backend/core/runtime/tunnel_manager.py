import asyncio
from typing import ClassVar

from backend import config
from backend.core.dto.tunnel_status import TunnelStatus
from backend.core.logger import setup_logger
from backend.features.realtime import notify
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

    _provider: ClassVar[TunnelProvider | None] = None
    _config = config.toml.tunnel
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    def _get_provider(cls, provider_name: str) -> TunnelProvider:
        provider_class = AVAILABLE_PROVIDERS.get(provider_name)

        if provider_class is None:
            available = ", ".join(AVAILABLE_PROVIDERS.keys())
            raise ValueError(
                f"Provider '{provider_name}' não encontrado. "
                f"Providers disponíveis: {available}"
            )

        return provider_class()

    @classmethod
    async def start_tunnel(cls) -> TunnelStatus:
        """
        Inicia o túnel usando o provider configurado.

        Returns:
            TunnelStart com URL e provider
        """
        async with cls._lock:
            if cls._config.provider == "lan":
                raise ValueError(
                    "Provider LAN não suporta essa operação. "
                    "Configure um provider ativo em config.toml "
                    "(localtunnel, playit, zrok)"
                )

            if cls._provider is not None and cls._provider.is_active():
                logger.warning("Túnel já está ativo")
                url = cls._provider.get_public_url() or ""
                return TunnelStatus(active=True, url=url, provider=cls._provider.name)

            try:
                # Instancia provider se necessário
                if cls._provider is None:
                    cls._provider = cls._get_provider(cls._config.provider)

                # Inicia túnel
                url = await cls._provider.start(cls._config.port)

            except Exception as e:
                logger.exception("❌ Erro ao iniciar túnel")
                notify("tunnel_error", {"message": str(e)})
                raise
            else:
                logger.info(
                    f"✅ Túnel iniciado com sucesso: {url} (provider: {cls._provider.name})"
                )

                # Notifica clientes via realtime
                notify(
                    "tunnel_started",
                    {
                        "url": url,
                        "provider": cls._provider.name,
                    },
                )

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
                    "(localtunnel, playit, zrok)"
                )

            if cls._provider is None or not cls._provider.is_active():
                raise ValueError("Nenhum túnel ativo para parar")

            try:
                await cls._provider.stop()
                logger.info("🔌 Túnel parado com sucesso")

                notify("tunnel_stopped", {})

            except Exception as e:
                logger.exception("❌ Erro ao parar túnel")
                notify("tunnel_error", {"message": str(e)})
                raise

    @classmethod
    def get_status(cls) -> TunnelStatus:
        """
        Retorna status atual do túnel.

        Para LAN: inicializa detecção de IPs ao primeiro acesso.

        Returns:
            TunnelStatus com status atual, URL e provider
        """
        # Garante que provider LAN está inicializado para detectar IPs
        if cls._provider is None and cls._config.provider == "lan":
            cls._provider = cls._get_provider("lan")

            # Inicializa IPs se for LANProvider
            if isinstance(cls._provider, LANProvider):
                cls._provider._initialize_ips()
                cls._provider._port = cls._config.port
                cls._provider._initialized = True

        is_active = cls._provider is not None and cls._provider.is_active()

        provider_url = None
        if is_active and cls._provider is not None:
            provider_url = cls._provider.get_public_url()

        return TunnelStatus(
            active=is_active,
            url=provider_url,
            provider=cls._provider.name if cls._provider is not None else None,
        )

    @classmethod
    def get_public_url(cls) -> str | None:
        """Retorna apenas a URL pública se túnel estiver ativo."""
        if cls._provider is None:
            return None

        return cls._provider.get_public_url()
