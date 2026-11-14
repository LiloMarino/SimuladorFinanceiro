import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal

from backend.core.dto.order import OrderDTO
from backend.core.enum import OrderAction, OrderStatus, OrderType
from backend.core.runtime.user_manager import UserManager

# Dono das ordens da liquidez do mercado simulado, que não é um jogador
MARKET_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__MARKET__")
# Dono da escada de compra e venda que o formador de mercado põe em volta do valor justo da cota
FUND_MAKER_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__FUND_MAKER__")
# Dono da ordem de venda da oferta pública das cotas de uma gestora
FUND_ISSUER_CLIENT_ID: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_DNS, "__FUND_ISSUER__")

# Os donos sintéticos e o apelido que cada um mostra no livro de ofertas
SYNTHETIC_NICKNAMES: dict[uuid.UUID, str] = {
    MARKET_CLIENT_ID: "Mercado",
    FUND_MAKER_CLIENT_ID: "Formador de mercado",
    FUND_ISSUER_CLIENT_ID: "Oferta pública",
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
        synthetic_nickname = SYNTHETIC_NICKNAMES.get(self.client_id)
        synthetic = synthetic_nickname is not None
        color = None
        is_bot = False
        if synthetic_nickname is not None:
            nickname = synthetic_nickname
        else:
            user = UserManager.get_user(self.client_id)
            nickname = "Unknown" if user is None else user.nickname
            color = None if user is None else UserManager.get_color(user.id)
            is_bot = user is not None and user.is_bot
        return OrderDTO(
            id=self.id,
            player_nickname=nickname,
            player_color=color,
            player_is_bot=is_bot,
            action=self.action,
            order_type=OrderType.LIMIT
            if isinstance(self, LimitOrder)
            else OrderType.MARKET,
            limit_price=getattr(self, "price", None),
            size=self.size,
            remaining=self.remaining,
            status=self.status,
            placed_on=self.placed_on,
            synthetic=synthetic,
        )


@dataclass(kw_only=True)
class MarketOrder(Order):
    # Compra por valor: o dinheiro que ainda pode ser gasto; cada execução desconta o que custou
    budget: Decimal | None = None


@dataclass(kw_only=True)
class LimitOrder(Order):
    price: float
    # Como taker, executa ao preço da própria ordem, e não ao da ordem do livro que ela casa
    fills_at_own_price: bool = False
