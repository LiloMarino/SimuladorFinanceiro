"""A configuração de um backtest: validação, regras da partida que ela vira e o caminho de volta."""

from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.backtest import (
    BacktestConfigDTO,
    BacktestCoverageDTO,
    BacktestParticipantDTO,
    BacktestSetupDTO,
)
from backend.core.dto.series_coverage import SeriesKind
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import BacktestPriceImpact, GameType, IndicatorSeries
from backend.core.exceptions.http_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.player_colors import PLAYER_COLORS
from backend.core.runtime.user_manager import BotConfig, UserManager
from backend.core.utils import next_business_day
from backend.features.import_data.coverage import get_series_coverage
from backend.features.simulation.saved_bots import saved_bots
from backend.features.statistics.score import MIN_SCORE_DAYS

# Os mesmos níveis do impacto de preço da folha de regras: (k, dias de decaimento)
PRICE_IMPACT_LEVELS: dict[BacktestPriceImpact, tuple[float, int]] = {
    BacktestPriceImpact.REALISTIC: (0.02, 20),
    BacktestPriceImpact.STRONG: (0.05, 40),
}

DEFAULT_NAME = "Backtest"
RATE_SERIES = {
    IndicatorSeries.CDI.value,
    IndicatorSeries.SELIC.value,
    IndicatorSeries.IPCA.value,
}


def coverage() -> BacktestCoverageDTO:
    """
    O primeiro dia em que CDI, SELIC e IPCA existem e já há ação cadastrada, e até
    onde o mercado é real e gerado: o que o período do backtest pode cobrir.
    """
    series = get_series_coverage()
    rates = [s.start for s in series if s.key in RATE_SERIES and s.start]
    stocks = [s for s in series if s.kind is SeriesKind.STOCK]
    starts = [s.start for s in stocks if s.start]
    first = max([*rates, min(starts)]) if starts and rates else None
    real_ends = [s.real_end for s in stocks if s.real_end]
    generated_ends = [s.generated_end for s in stocks if s.generated_end]
    return BacktestCoverageDTO(
        first_date=first,
        real_end=max(real_ends) if real_ends else None,
        generated_end=max(generated_ends) if generated_ends else None,
    )


def trading_days(start: date, end: date) -> int:
    """Quantos pregões a partida joga: os mesmos dias que o motor percorre."""
    count = 0
    day = next_business_day(start - timedelta(days=1))
    while day <= end:
        count += 1
        day = next_business_day(day)
    return count


def resolve(
    config: BacktestConfigDTO,
) -> list[tuple[BacktestParticipantDTO, BotConfig]]:
    """
    Confere o que depende do banco e do catálogo e devolve cada participante com os
    parâmetros completos. Qualquer problema sai como 422, antes de gravar algo.
    """
    available = coverage()
    if available.first_date is None:
        raise UnprocessableEntityError("Não há dados de mercado para o backtest.")
    if config.start_date < available.first_date:
        raise UnprocessableEntityError(
            f"O mercado começa em {available.first_date:%d/%m/%Y}."
        )
    last = available.generated_end or available.real_end
    if last is not None and config.end_date > last:
        raise UnprocessableEntityError(f"O mercado vai até {last:%d/%m/%Y}.")
    if trading_days(config.start_date, config.end_date) < MIN_SCORE_DAYS:
        raise UnprocessableEntityError(
            f"O período precisa ter ao menos {MIN_SCORE_DAYS} pregões para a nota fazer sentido."
        )

    resolved: list[tuple[BacktestParticipantDTO, BotConfig]] = []
    names: set[str] = set()
    colors: set[str] = set()
    for participant in config.participants:
        nickname = UserManager.bot_nickname(participant.nickname)
        if nickname.casefold() in names:
            raise UnprocessableEntityError(f"Dois participantes se chamam {nickname}.")
        if participant.color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")
        if participant.color in colors:
            raise UnprocessableEntityError("Dois participantes usam a mesma cor.")
        names.add(nickname.casefold())
        colors.add(participant.color)
        bot = UserManager.bot_config(
            participant.strategy_key, participant.params, config.start_date
        )
        resolved.append(
            (
                participant.model_copy(
                    update={"nickname": nickname, "params": bot.params}
                ),
                bot,
            )
        )
    return resolved


def settings_of(config: BacktestConfigDTO) -> SimulationSettingsDTO:
    """As regras da partida do backtest: só saldo, aporte e impacto de preço valem."""
    enabled = config.price_impact is not BacktestPriceImpact.OFF
    k, decay = PRICE_IMPACT_LEVELS.get(config.price_impact, (0.0, 1))
    return SimulationSettingsDTO.model_validate(
        {
            "name": config.name,
            "start_date": config.start_date,
            "end_date": config.end_date,
            "starting_cash": config.starting_cash,
            "monthly_contribution": config.monthly_contribution,
            "price_impact_enabled": enabled,
            "price_impact_k": k,
            "price_impact_decay_days": decay,
            "victory_criterion": "SCORE",
            "game_type": GameType.CLASSIC,
            # Sem efeito na Clássica
            "goal_net_worth": config.starting_cash,
            "monthly_salary": Decimal(0),
            "monthly_expense": Decimal(0),
            "unexpected_per_year": 0,
            "withdrawal_rate": Decimal("0.04"),
            "inflation_adjusted": False,
        }
    )


def config_of(simulation_id: int) -> BacktestConfigDTO:
    """A configuração de um backtest salvo, remontada das regras e dos bots que ele gravou."""
    summary = repository.simulation.get_simulation(simulation_id)
    if summary is None or not summary.is_backtest:
        raise NotFoundError("Backtest não encontrado.")
    colors = repository.simulation_player.colors(simulation_id)
    participants = [
        BacktestParticipantDTO(
            nickname=bot.nickname,
            color=colors[bot.id],
            strategy_key=config.strategy_key,
            params=config.params,
        )
        for bot, config in sorted(saved_bots(simulation_id), key=lambda b: b[0].id)
    ]
    return BacktestConfigDTO(
        name=summary.name,
        start_date=summary.start_date,
        end_date=summary.end_date,
        starting_cash=summary.starting_cash,
        monthly_contribution=summary.monthly_contribution,
        price_impact=_level_of(summary),
        participants=participants,
    )


def _level_of(settings: SimulationSettingsDTO) -> BacktestPriceImpact:
    if not settings.price_impact_enabled:
        return BacktestPriceImpact.OFF
    for level, (k, decay) in PRICE_IMPACT_LEVELS.items():
        if (settings.price_impact_k, settings.price_impact_decay_days) == (k, decay):
            return level
    return BacktestPriceImpact.REALISTIC


def unique_name(base: str) -> str:
    """O nome da partida é único no banco: ganha " (2)", " (3)"… até ficar livre."""
    taken = {s.name for s in repository.simulation.list_simulations()}
    name, n = base, 1
    while name in taken:
        n += 1
        name = f"{base} ({n})"
    return name


def setup(from_id: int | None) -> BacktestSetupDTO:
    """
    A cobertura e a configuração de partida: a do backtest indicado (rodar de novo)
    ou a do mais recente, com o nome livre; sem nenhum, a tela abre vazia.
    """
    source = from_id
    if source is None:
        latest = next(
            (s for s in repository.simulation.list_simulations() if s.is_backtest),
            None,
        )
        source = latest.id if latest else None
    previous = config_of(source) if source is not None else None
    return BacktestSetupDTO(
        coverage=coverage(),
        config=(
            previous.model_copy(update={"name": unique_name(previous.name)})
            if previous
            else None
        ),
        suggested_name=unique_name(DEFAULT_NAME),
    )
