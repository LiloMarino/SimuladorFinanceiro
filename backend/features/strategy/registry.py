from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.cdi import CdiReference
from backend.features.strategy.moving_average import MovingAverageCross

# As estratégias do app, na ordem da lista: referências e depois táticas
STRATEGIES: dict[str, type[BaseStrategy]] = {
    strategy.key: strategy for strategy in (CdiReference, MovingAverageCross)
}


def get_strategy(key: str) -> type[BaseStrategy]:
    strategy = STRATEGIES.get(key)
    if strategy is None:
        raise UnprocessableEntityError(f"Estratégia desconhecida: {key}.")
    return strategy
