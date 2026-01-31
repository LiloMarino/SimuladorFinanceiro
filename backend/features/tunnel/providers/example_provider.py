import uuid

from backend.core.logger import setup_logger
from backend.features.tunnel.tunnel_provider import TunnelProvider

logger = setup_logger(__name__)


class ExampleProvider(TunnelProvider):
    """
    Provider mock para desenvolvimento e testes.

    Responsável por:
    - Gerar URLs mock sem criar conexões reais
    - Simular lifecycle de túnel (start/stop) para prototipagem
    - Fornecer placeholder para testes locais sem infraestrutura externa

    ⚠️ Não cria túneis reais! Apenas para desenvolvimento.
    """

    def __init__(self):
        self._active = False
        self._url: str | None = None

    @property
    def name(self) -> str:
        return "example"

    async def start(self, port: int) -> str:
        """Simula criação de túnel gerando URL mock."""
        if self._active:
            logger.warning("Túnel example já está ativo")
            return self._url  # type: ignore

        # Gera URL mock única
        tunnel_id = str(uuid.uuid4())[:8]
        self._url = f"https://tunnel-example-{tunnel_id}.example.com"
        self._active = True

        logger.info(f"🔗 Túnel example iniciado (MOCK): {self._url}")
        logger.warning(
            "⚠️  Este é um túnel EXAMPLE - não cria conexão real! "
            "Implemente um provider real para funcionalidade completa."
        )

        return self._url

    async def stop(self) -> None:
        """Para o túnel example."""
        if not self._active:
            logger.warning("Nenhum túnel example ativo para parar")
            return

        logger.info(f"🔌 Túnel example parado: {self._url}")
        self._active = False
        self._url = None

    def get_public_url(self) -> str | None:
        """Retorna a URL mock se ativo."""
        return self._url if self._active else None

    def is_active(self) -> bool:
        """Verifica se o túnel está ativo."""
        return self._active
