from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.breakout import VolumeBreakout
from backend.features.strategy.buy_and_hold import BuyAndHold
from backend.features.strategy.cdi import CdiReference
from backend.features.strategy.momentum import TwelveMonthMomentum
from backend.features.strategy.moving_average import MovingAverageCross
from backend.features.strategy.rebalance import TargetRebalance
from backend.features.strategy.rsi import RelativeStrength

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
    )
}


def get_strategy(key: str) -> type[BaseStrategy]:
    strategy = STRATEGIES.get(key)
    if strategy is None:
        raise UnprocessableEntityError(f"Estratégia desconhecida: {key}.")
    return strategy
