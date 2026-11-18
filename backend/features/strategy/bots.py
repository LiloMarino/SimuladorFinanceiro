from datetime import date

from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import Profession
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.professions import available_bot_professions
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import BotConfig, UserManager
from backend.features.strategy import catalog
from backend.features.strategy.registry import ensure_available, get_strategy


def resolve_bot(
    strategy_key: str,
    params: dict[str, StrategyParamValue],
    today: date | None = None,
    profession: Profession | None = None,
    funds_enabled: bool | None = None,
) -> BotConfig:
    """Os parâmetros completos pelo catálogo, na data das regras do lobby, e já validados; a profissão, quando fixa, é uma que a sala permite.

    A estratégia que exige a expansão Gestoras vale só onde ela existe: `funds_enabled` nulo
    segue as regras da sala.
    """
    if profession is not None and profession not in available_bot_professions(
        inflation_adjusted=SettingsManager.effective_inflation_adjusted(),
        government_enabled=SettingsManager.effective_government_enabled(),
        funds_enabled=SettingsManager.effective_funds_enabled(),
    ):
        raise UnprocessableEntityError("Essa profissão não existe nas regras da sala.")
    strategy = get_strategy(strategy_key)
    ensure_available(
        strategy,
        funds_enabled=SettingsManager.effective_funds_enabled()
        if funds_enabled is None
        else funds_enabled,
    )
    known = catalog.known_tickers()
    resolved = catalog.with_defaults(
        strategy, params, today or SettingsManager.get().start_date, None, known
    )
    errors = strategy.validate(resolved, known)
    if errors:
        raise UnprocessableEntityError(" ".join(errors.values()))
    return BotConfig(strategy_key, strategy.name, resolved, profession=profession)


def validate_room_bots(start_date: date) -> None:
    """Conferido ao iniciar: as regras podem ter mudado desde que o bot entrou na sala."""
    for bot, config in UserManager.room_bots():
        try:
            resolve_bot(config.strategy_key, config.params, start_date)
        except UnprocessableEntityError as error:
            raise UnprocessableEntityError(
                f"{bot.nickname} não joga com as regras de agora: {error.detail}"
            ) from error
