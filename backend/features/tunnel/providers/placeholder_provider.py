import uuid

from backend.core.logger import setup_logger
from backend.features.tunnel.tunnel_provider import TunnelProvider

logger = setup_logger(__name__)


class PlaceholderProvider(TunnelProvider):
    """
    Provider de placeholder que não cria túnel real.

    Útil para desenvolvimento e testes. Gera URLs mock no formato:
    https://tunnel-placeholder-{uuid}.example.com

    ⚠️ Este provider não cria conexões reais! É apenas para prototipagem.
    Para expor o servidor publicamente, implemente um provider real
    (ex: LocalTunnel, ngrok, etc).
    """

    def __init__(self):
        self._active = False
        self._url: str | None = None

    @property
    def name(self) -> str:
        return "placeholder"

    async def start(self, port: int) -> str:
        """Simula criação de túnel gerando URL mock."""
        if self._active:
            logger.warning("Túnel placeholder já está ativo")
            return self._url  # type: ignore

        # Gera URL mock única
        tunnel_id = str(uuid.uuid4())[:8]
        self._url = f"https://tunnel-placeholder-{tunnel_id}.example.com"
        self._active = True

        logger.info(f"🔗 Túnel placeholder iniciado (MOCK): {self._url}")
        logger.warning(
            "⚠️  Este é um túnel PLACEHOLDER - não cria conexão real! "
            "Implemente um provider real para funcionalidade completa."
        )

        return self._url

    async def stop(self) -> None:
        """Para o túnel placeholder."""
        if not self._active:
            logger.warning("Nenhum túnel placeholder ativo para parar")
            return

        logger.info(f"🔌 Túnel placeholder parado: {self._url}")
        self._active = False
        self._url = None

    def get_public_url(self) -> str | None:
        """Retorna a URL mock se ativo."""
        return self._url if self._active else None

    def is_active(self) -> bool:
        """Verifica se o túnel está ativo."""
        return self._active
