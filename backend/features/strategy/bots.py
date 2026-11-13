from datetime import date

from backend.core.dto.strategy import StrategyParamValue
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import BotConfig, UserManager
from backend.features.strategy import catalog
from backend.features.strategy.registry import get_strategy


def resolve_bot(
    strategy_key: str,
    params: dict[str, StrategyParamValue],
    today: date | None = None,
) -> BotConfig:
    """Os parâmetros completos pelo catálogo, na data das regras do lobby, e já validados."""
    strategy = get_strategy(strategy_key)
    known = catalog.known_tickers()
    resolved = catalog.with_defaults(
        strategy, params, today or SettingsManager.get().start_date, None, known
    )
    errors = strategy.validate(resolved, known)
    if errors:
        raise UnprocessableEntityError(" ".join(errors.values()))
    return BotConfig(strategy_key, strategy.name, resolved)


def validate_room_bots(start_date: date) -> None:
    """Conferido ao iniciar: as regras podem ter mudado desde que o bot entrou na sala."""
    for bot, config in UserManager.room_bots():
        try:
            resolve_bot(config.strategy_key, config.params, start_date)
        except UnprocessableEntityError as error:
            raise UnprocessableEntityError(
                f"{bot.nickname} não joga com as regras de agora: {error.detail}"
            ) from error
