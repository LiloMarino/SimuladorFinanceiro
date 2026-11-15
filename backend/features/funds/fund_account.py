from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from backend.features.market_maker.account import MakerAccount


@dataclass(kw_only=True)
class FundAccount(MakerAccount):
    """A conta de uma cota de gestora: o que o formador move e o que a oferta e a recompra movem."""

    # A conta da gestora no motor, que recebe o dinheiro da oferta
    client_id: UUID
    # Nulo sem oferta aberta
    offer_remaining: Decimal | None = None

    def issue(self, size: Decimal) -> None:
        """A oferta vendeu `size` cotas: elas passam a existir e saem do saldo da oferta.

        Sem saldo a vender a oferta está encerrada: `offer_remaining` volta a ser nulo.
        """
        if self.offer_remaining is None or size > self.offer_remaining:
            raise ValueError("Não há oferta aberta para emitir essa quantidade")
        self.quotas += size
        self.offer_remaining -= size
        if self.offer_remaining <= 0:
            self.offer_remaining = None

    def subscribe(self, size: Decimal) -> None:
        """A preferência da emissão: `size` cotas passam a existir para quem as comprou direto."""
        self.quotas += size

    def burn(self, size: Decimal) -> None:
        """A recompra comprou `size` cotas: elas deixam de existir."""
        if size > self.quotas:
            raise ValueError("Não há essa quantidade de cotas para recomprar")
        self.quotas -= size
