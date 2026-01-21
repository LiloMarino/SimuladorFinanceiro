"""Abstract base class for tunnel providers."""

from abc import ABC, abstractmethod


class TunnelProvider(ABC):
    """
    Interface abstrata para provedores de túnel de rede.

    Cada provider (LocalTunnel, ngrok, Tailscale, etc) deve implementar esta interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome identificador do provider (ex: 'localtunnel', 'ngrok')."""
        pass

    @abstractmethod
    async def start(self, port: int) -> str:
        """
        Inicia o túnel na porta especificada.

        Args:
            port: Porta local a ser exposta

        Returns:
            URL pública do túnel (ex: 'https://abc123.loca.lt')

        Raises:
            Exception: Se falhar ao criar o túnel
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Para o túnel ativo.

        Raises:
            Exception: Se falhar ao parar o túnel
        """
        pass

    @abstractmethod
    def get_public_url(self) -> str | None:
        """
        Retorna a URL pública do túnel se estiver ativo.

        Returns:
            URL pública ou None se não houver túnel ativo
        """
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """
        Verifica se o túnel está ativo.

        Returns:
            True se o túnel estiver rodando, False caso contrário
        """
        pass
