import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal

from backend.core.dto.order import OrderDTO
from backend.core.enum import OrderAction, OrderOwner, OrderStatus, OrderType
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager

# Dono das ordens da liquidez do mercado simulado, que não é um jogador
MARKET_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__MARKET__")
# Dono da escada de compra e venda que o formador de mercado põe em volta do valor justo da cota
FUND_MAKER_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__FUND_MAKER__")
# Dono da ordem de venda da oferta pública das cotas de uma gestora
FUND_ISSUER_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__FUND_ISSUER__")

# Os donos sintéticos, o apelido que cada um mostra no livro de ofertas e o tipo de dono
SYNTHETIC_OWNERS: dict[uuid.UUID, tuple[str, OrderOwner]] = {
    MARKET_CLIENT_ID: ("Mercado", OrderOwner.MARKET),
    FUND_MAKER_CLIENT_ID: ("Formador de mercado", OrderOwner.FUND_MAKER),
    FUND_ISSUER_CLIENT_ID: ("Oferta pública", OrderOwner.FUND_ISSUER),
}


@dataclass(kw_only=True)
class Order(ABC):
    """Representa uma ordem de compra ou venda executada ou pendente."""

    client_id: uuid.UUID
    ticker: str
    size: Decimal
    action: OrderAction
    # O dia da partida em que a ordem nasceu; created_at é o relógio real e só ordena a fila
    placed_on: date
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    remaining: Decimal = field(init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: OrderStatus = OrderStatus.PENDING
    # Ordem enviada por uma estratégia: o aviso dela é o do registro da estratégia
    automatic: bool = False
    # Soma de quantidade x preço das execuções, para o preço médio
    notional: float = 0.0

    def __post_init__(self):
        self.remaining = self.size

    def to_dto(self) -> OrderDTO:
        nickname, owner, color = self._owner()
        return OrderDTO(
            id=self.id,
            player_nickname=nickname,
            player_color=color,
            owner=owner,
            action=self.action,
            order_type=OrderType.LIMIT
            if isinstance(self, LimitOrder)
            else OrderType.MARKET,
            limit_price=getattr(self, "price", None),
            size=self.size,
            remaining=self.remaining,
            status=self.status,
            placed_on=self.placed_on,
        )

    def _owner(self) -> tuple[str, OrderOwner, str | None]:
        """O apelido, o tipo de dono e a cor da paleta de quem pôs a ordem."""
        synthetic = SYNTHETIC_OWNERS.get(self.client_id)
        if synthetic is not None:
            return (*synthetic, None)
        fund_name = SimulationManager.find_fund_name(self.client_id)
        if fund_name is not None:
            return fund_name, OrderOwner.FUND, None
        user = UserManager.get_user(self.client_id)
        if user is None:
            return "Unknown", OrderOwner.PLAYER, None
        owner = OrderOwner.BOT if user.is_bot else OrderOwner.PLAYER
        return user.nickname, owner, UserManager.get_color(user.id)


@dataclass(kw_only=True)
class MarketOrder(Order):
    # Compra por valor: o dinheiro que ainda pode ser gasto; cada execução desconta o que custou
    budget: Decimal | None = None


@dataclass(kw_only=True)
class LimitOrder(Order):
    price: float
    # Como taker, executa ao preço da própria ordem, e não ao da ordem do livro que ela casa
    fills_at_own_price: bool = False
