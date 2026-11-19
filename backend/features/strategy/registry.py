from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.professions import Expansion
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.breakout import VolumeBreakout
from backend.features.strategy.buy_and_hold import BuyAndHold
from backend.features.strategy.cdi import CdiReference
from backend.features.strategy.fund_quotas import FundQuotas
from backend.features.strategy.momentum import TwelveMonthMomentum
from backend.features.strategy.moving_average import MovingAverageCross
from backend.features.strategy.rebalance import TargetRebalance
from backend.features.strategy.rsi import RelativeStrength
from backend.features.strategy.state_companies import StateCompanies

# As estratégias do app, na ordem da lista: referências e depois táticas
STRATEGIES: dict[str, type[BaseStrategy]] = {
    strategy.key: strategy
    for strategy in (
        BuyAndHold,
        CdiReference,
        TargetRebalance,
        MovingAverageCross,
        RelativeStrength,
        VolumeBreakout,
        TwelveMonthMomentum,
        FundQuotas,
        StateCompanies,
    )
}


# O nome de cada expansão como o jogador a conhece
EXPANSION_NAMES = {Expansion.FUNDS: "Gestoras", Expansion.GOVERNMENT: "Governo"}


def ensure_available(
    strategy: type[BaseStrategy], *, funds_enabled: bool, government_enabled: bool
) -> None:
    """Recusa a estratégia que exige uma expansão que a sala não tem."""
    if not strategy.available(
        funds_enabled=funds_enabled, government_enabled=government_enabled
    ):
        expansion = strategy.requires_expansion
        label = EXPANSION_NAMES[expansion] if expansion else ""
        raise UnprocessableEntityError(
            f"{strategy.name} exige a expansão {label}, que esta sala não tem."
        )


def get_strategy(key: str) -> type[BaseStrategy]:
    strategy = STRATEGIES.get(key)
    if strategy is None:
        raise UnprocessableEntityError(f"Estratégia desconhecida: {key}.")
    return strategy
