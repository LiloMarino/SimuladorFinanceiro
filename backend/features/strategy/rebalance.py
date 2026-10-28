from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.dto.strategy import (
    AllocationItemDTO,
    AllocationViewDTO,
    RankingViewDTO,
    StrategyParamValue,
)
from backend.core.enum import (
    RateIndexType,
    StrategyGroup,
    StrategyParamKind,
    StrategyView,
)
from backend.core.utils import format_money, format_quantity, required
from backend.features.strategy.allocation import Item, distribute, whole_shares
from backend.features.strategy.base_strategy import (
    BaseStrategy,
    ParamSpec,
    param_int,
    param_ticker,
)
from backend.features.strategy.buy_and_hold import DEFAULT_ASSET
from backend.features.strategy.context import StrategyContext

ZERO = Decimal(0)
CENT = Decimal("0.01")
TENTH = Decimal("0.1")
# Abaixo disto o dinheiro parado não vale uma ordem
MIN_MOVE = Decimal(1)


@dataclass(frozen=True)
class _Holdings:
    """A carteira da estratégia, de cada lado, e a parte de cada lado que ela não mexe."""

    stock_value: Decimal
    stock_floor: Decimal
    fixed_value: Decimal
    fixed_floor: Decimal

    @property
    def total(self) -> Decimal:
        return self.stock_value + self.fixed_value

    def stock_share(self) -> Decimal:
        """Fração das ações na carteira; zero sem nada investido."""
        return self.stock_value / self.total if self.total > 0 else ZERO


class TargetRebalance(BaseStrategy):
    """
    Mantém a carteira na divisão escolhida entre um ativo de renda variável e a renda
    fixa de liquidez diária. Todo dia confere o desvio das ações contra a meta: acima do
    limite, vende ou resgata para voltar à meta; dentro dele, o caixa parado é um aporte
    que vai primeiro para o lado mais abaixo da meta.
    """

    key = "target_rebalance"
    name = "Rebalanceamento por meta"
    bot_names = ("Equilibrista", "Mestre da Meta", "Balanceado")
    summary = "Volta à divisão escolhida quando ela sai da meta."
    description = (
        "Mantém uma divisão entre ações e renda fixa de liquidez diária. Quando as "
        "ações passam do limite de desvio da meta, vende ou resgata para voltar a ela; "
        "dentro do limite, o caixa parado vai para o lado mais abaixo da meta."
    )
    group = StrategyGroup.REFERENCE
    view_kind = StrategyView.ALLOCATION
    term_hint = (
        "Rebalancear é voltar à divisão que você escolheu. p.p. é a diferença entre "
        "dois percentuais: 66% de ações contra a meta de 60% são 6 p.p. acima."
    )
    params = (
        ParamSpec(
            key="asset",
            label="Ativo",
            kind=StrategyParamKind.TICKER,
            default=DEFAULT_ASSET,
            hint=(
                "A ação ou o ETF que representa o lado das ações: é a única que a "
                "estratégia compra e vende. O padrão é o BOVA11; se a partida não tem "
                "o BOVA11, o padrão é a ação mais negociada dela."
            ),
        ),
        ParamSpec(
            key="stock_target",
            label="Meta em ações",
            kind=StrategyParamKind.INT,
            default=60,
            min=10,
            max=90,
            unit="%",
            hint=(
                "Quanto da carteira fica nas ações; a renda fixa fica com o resto. "
                "Com 60%, R$ 10.000 viram R$ 6.000 em ações e R$ 4.000 na renda fixa."
            ),
        ),
        ParamSpec(
            key="max_deviation",
            label="Desvio máximo",
            kind=StrategyParamKind.INT,
            default=5,
            min=1,
            max=20,
            unit="p.p.",
            hint=(
                "Quanto as ações podem se afastar da meta antes de a estratégia vender "
                "ou resgatar. Com meta de 60% e limite de 5 p.p., ela age quando as "
                "ações passam de 65% ou caem de 55%. Quanto menor, mais ordens (e mais "
                "custo)."
            ),
        ),
    )

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        asset = param_ticker(params, "asset")
        target = Decimal(param_int(params, "stock_target")) / 100
        limit = Decimal(param_int(params, "max_deviation")) / 100
        held = _holdings(ctx, asset)

        # Fora do limite a carteira volta à meta com venda e resgate; dentro dele só o
        # caixa se move, e nenhum lado desce do valor de hoje
        rebalancing = held.total > 0 and abs(held.stock_share() - target) > limit
        if not rebalancing and ctx.cash < MIN_MOVE:
            return

        stock_floor = held.stock_floor if rebalancing else held.stock_value
        fixed_floor = held.fixed_floor if rebalancing else held.fixed_value
        new_stock, new_fixed = distribute(
            [
                Item(value=held.stock_value, target=target, floor=stock_floor),
                Item(value=held.fixed_value, target=1 - target, floor=fixed_floor),
            ],
            ctx.cash,
        )
        stock_move = new_stock - held.stock_value
        fixed_move = new_fixed - held.fixed_value
        why = _why(held, target, rebalancing)

        # Cada ordem conta com o caixa que as anteriores deixam
        available = ctx.cash
        if fixed_move <= -MIN_MOVE:
            available += _redeem(ctx, -fixed_move, why)

        quote = ctx.quotes.get(asset)
        if quote is not None:
            price = Decimal(str(quote.close))
            shares = whole_shares(stock_move, price, fractional=quote.fractional)
            if stock_move < 0:
                holding = ctx.holdings.get(asset)
                shares = (
                    min(shares, holding.size - holding.reserved) if holding else ZERO
                )
                if shares > 0:
                    ctx.sell(
                        asset,
                        shares,
                        f"{why}: vendeu {format_quantity(shares)} {asset}",
                    )
                    available += price * shares
            elif stock_move > 0:
                shares = min(shares, ctx.affordable(asset, available))
                if shares > 0:
                    ctx.buy(
                        asset,
                        shares,
                        f"{why}: comprou {format_quantity(shares)} {asset}",
                    )
                    available -= price * shares

        offer = _liquid_offer(ctx)
        value = min(fixed_move, available).quantize(CENT, ROUND_DOWN)
        if offer is not None and value >= MIN_MOVE:
            ctx.invest(
                offer.asset_uuid,
                value,
                f"{why}: aplicou {format_money(value)} em {offer.name}",
            )

    def view(
        self, ctx: StrategyContext, params: dict[str, StrategyParamValue]
    ) -> RankingViewDTO | AllocationViewDTO | None:
        asset = param_ticker(params, "asset")
        target = Decimal(param_int(params, "stock_target"))
        held = _holdings(ctx, asset)

        def item(label: str, value: Decimal, goal: Decimal) -> AllocationItemDTO:
            current = value / held.total * 100 if held.total > 0 else ZERO
            return AllocationItemDTO(
                label=label,
                value=value.quantize(CENT),
                current_pct=current.quantize(TENTH),
                target_pct=goal.quantize(TENTH),
                deviation_pp=(current - goal).quantize(TENTH),
            )

        # O que ela faria hoje sai da própria regra, sobre uma fila de intenções vazia
        self.next(ctx, params)
        return AllocationViewDTO(
            items=[
                item(f"Ações ({asset})", held.stock_value, target),
                item("Renda fixa", held.fixed_value, 100 - target),
            ],
            limit_pp=param_int(params, "max_deviation"),
            has_liquid_offer=_liquid_offer(ctx) is not None,
            today=[intent.reason for intent in ctx.intents],
        )


def _holdings(ctx: StrategyContext, asset: str) -> _Holdings:
    """
    Valor a preço de hoje de cada lado. O piso é o que a estratégia não mexe: as ações
    que não são o ativo, a parte do ativo presa em ordens abertas e os títulos sem
    liquidez diária.
    """
    stock_value = ZERO
    stock_floor = ZERO
    for ticker, holding in ctx.holdings.items():
        quote = ctx.quotes.get(ticker)
        price = Decimal(str(quote.close)) if quote else holding.avg_price
        stock_value += price * holding.size
        stock_floor += price * (holding.reserved if ticker == asset else holding.size)

    fixed_value = sum((h.current_value for h in ctx.fixed_holdings), ZERO)
    fixed_floor = sum(
        (h.current_value for h in ctx.fixed_holdings if not h.daily_liquidity), ZERO
    )
    return _Holdings(stock_value, stock_floor, fixed_value, fixed_floor)


def _liquid_offer(ctx: StrategyContext) -> FixedIncomeOfferDTO | None:
    """O CDB de liquidez diária sem teto por jogador: o que comporta o caixa inteiro."""
    offers = [
        o
        for o in ctx.fixed_offers
        if o.daily_liquidity
        and o.rate_index is RateIndexType.CDI
        and o.player_cap is None
    ]
    if not offers:
        return None
    return min(offers, key=lambda o: (-o.interest_rate, str(o.asset_uuid)))


def _redeem(ctx: StrategyContext, need: Decimal, why: str) -> Decimal:
    """Resgata `need` dos títulos de liquidez diária, os maiores primeiro; devolve o resgatado."""
    redeemed = ZERO
    liquid = sorted(
        (h for h in ctx.fixed_holdings if h.redeemable),
        key=lambda h: (-(h.redeemable or ZERO), str(h.asset_uuid)),
    )
    for holding in liquid:
        value = min(need - redeemed, required(holding.redeemable)).quantize(
            CENT, ROUND_DOWN
        )
        if value < MIN_MOVE:
            continue
        ctx.redeem(
            holding.asset_uuid,
            value,
            f"{why}: resgatou {format_money(value)} de {holding.name}",
        )
        redeemed += value
    return redeemed


def _why(held: _Holdings, target: Decimal, rebalancing: bool) -> str:
    if not rebalancing:
        return "O caixa parado foi para o lado abaixo da meta"
    return (
        f"As ações estavam em {_percent(held.stock_share())} e a meta é "
        f"{_percent(target)}"
    )


def _percent(fraction: Decimal) -> str:
    return f"{fraction * 100:.1f}%".replace(".", ",")
