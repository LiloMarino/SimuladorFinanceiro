"""
Mede o dia do motor numa partida longa, sem dormir e sem Socket.IO: o antes e o depois
reproduzível de uma mudança de desempenho.

Uso: `pnpm profile:match --days 1000 --bots 5`. O script grava uma partida de rascunho,
roda os dias e a apaga ao fim. Com `--source <nome ou id>`, o rascunho copia as regras, os
jogadores e as estratégias de uma partida salva, que não é tocada. Sem ele, o rascunho é
uma partida clássica com `--bots` bots de estratégias diferentes. Como grava no banco,
o padrão é o banco de teste (`POSTGRES_TEST_DATABASE_URL` do `.env`); `--database current`
usa o que o ambiente aponta.

A saída tem a mediana e o p95 (o tempo que 95% dos dias não passam) de cada etapa nos
primeiros e nos últimos dias, e a razão entre as duas: perto de 1,0 o dia não cresce com
a partida. `--profile` grava o perfil do yappi em `profiles/`; nele as proporções valem e
os milissegundos não, porque ele mesmo custa tempo.
"""

import argparse
import logging
import statistics
import sys
import time
from collections import defaultdict
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend import config
from backend.config.env_settings import ENV_PATH
from backend.core import repository
from backend.core.dto.backtest import BacktestConfigDTO, BacktestParticipantDTO
from backend.core.dto.simulation import SimulationDTO, SimulationSettingsDTO
from backend.core.enum import BacktestPriceImpact
from backend.core.metrics import ENGINE_DAY, metrics
from backend.core.player_colors import PLAYER_COLORS
from backend.core.profiling import mark_engine_thread, profiler
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.backtest import config as backtest_config
from backend.features.realtime.realtime_broker import RealtimeBroker
from backend.features.simulation.simulation import Simulation
from backend.features.strategy.registry import STRATEGIES
from backend.features.strategy.state import derive_state
from backend.types import SID, ClientID, Event, JSONValue

DATABASE_CHOICES = ("test", "current")
SCRATCH_PREFIX = "profile-match-"
DEFAULT_DAYS = 1000
DEFAULT_BOTS = 5
# Dias das pontas da comparação (primeiros e últimos) e intervalo da curva de crescimento
DEFAULT_WINDOW = 50
DEFAULT_CHECKPOINT = 100
STARTING_CASH = Decimal(100_000)
MONTHLY_CONTRIBUTION = Decimal(2_000)
# Dias corridos por pregão, com folga: 1.000 pregões cabem em 1.000 * 7/5 dias
CALENDAR_PER_TRADING_DAY = 1.45


class ScratchDatabaseSettings(BaseSettings):
    url: str = Field(default="", alias="POSTGRES_TEST_DATABASE_URL")

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--source", help="nome ou id de uma partida salva para copiar")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--bots", type=int, default=DEFAULT_BOTS)
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    parser.add_argument("--checkpoint", type=int, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--database", choices=DATABASE_CHOICES, default="test")
    parser.add_argument("--profile", action="store_true")
    return parser.parse_args(argv)


def select_database(choice: str) -> None:
    """
    Define o banco antes do primeiro uso. A engine nasce na primeira consulta com a URL
    de `config.env`, que o import do backend já carregou do .env: é nela que vai o banco.
    """
    if choice == "current":
        return
    url = ScratchDatabaseSettings().url
    if not url:
        sys.exit(
            "POSTGRES_TEST_DATABASE_URL não está no .env (ou use --database current)."
        )
    config.env.postgres_url = url


def median_ms(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def p95_ms(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, -(-95 * len(ordered) // 100) - 1)] if ordered else 0.0


@dataclass
class Player:
    """Quem joga o rascunho e a estratégia dele (vazia é o modo manual)."""

    user_id: int
    color: str
    team: int | None = None
    strategy_key: str | None = None
    params: dict = field(default_factory=dict)


@dataclass
class Draft:
    settings: SimulationSettingsDTO
    players: list[Player]


class SilentBroker(RealtimeBroker):
    """Ninguém escuta: o dia monta cada evento e o descarta."""

    def update_subscription(self, sid: SID, events: Iterable[Event]) -> None:
        pass

    def notify(
        self, event: Event, payload: JSONValue, to: ClientID | None = None
    ) -> None:
        pass


def main(argv: list[str]) -> None:
    args = parse_args(argv)
    # A saída redirecionada para arquivo vai em UTF-8, também no Windows
    sys.stdout.reconfigure(encoding="utf-8")  # pyright: ignore[reportAttributeAccessIssue]
    select_database(args.database)
    logging.disable(logging.WARNING - 1)

    RealtimeBrokerManager.set_broker(SilentBroker())
    draft = copy_of(args.source) if args.source else recipe(args.days, args.bots)
    settings = draft.settings
    scratch_id = repository.simulation.create_simulation(settings)
    durations: dict[str, list[float]] = defaultdict(list)
    try:
        players = draft.players
        if not args.source:
            # Os bots do rascunho são usuários novos, apagados com ele
            for player in players:
                bot = repository.user.create_user(
                    uuid4(), f"Bot {player.color}", is_bot=True
                )
                player.user_id = bot.id
        repository.simulation_player.save(
            scratch_id,
            {p.user_id: p.color for p in players},
            {p.user_id: p.team for p in players if p.team is not None} or None,
        )
        repository.user.seed_simulation_users(
            scratch_id,
            [p.user_id for p in players],
            settings.start_date,
            settings.starting_cash,
        )
        participants = repository.simulation_player.participants(scratch_id)
        # Cada participante faz o papel de jogador conectado: o dia monta o
        # `portfolio_update` de cada um, como no jogo
        UserManager.list_active_players = classmethod(lambda cls: participants)  # pyright: ignore[reportAttributeAccessIssue]

        metrics.enabled = True
        metrics.record = lambda kind, name, ms: record(durations, kind, name, ms)  # pyright: ignore[reportAttributeAccessIssue]
        # O motor lê a partida ativa do gerenciador, como no jogo
        SimulationManager.set_simulation_id(scratch_id)
        sim = Simulation(
            SimulationDTO(id=scratch_id, **settings.model_dump()),
            random_seed=repository.simulation.get_random_seed(scratch_id),
        )
        SimulationManager.register_simulation(sim)
        by_id = {p.user_id: p for p in players}
        for user in participants:
            player = by_id[user.id]
            if player.strategy_key is not None:
                sim.set_my_strategy(user, player.strategy_key, player.params)
        durations.clear()

        mark_engine_thread()
        with profile_for(args.profile):
            run_days(sim, args.days, durations, ENGINE_DAY, args.checkpoint)
    finally:
        SimulationManager.clear_simulation()
        repository.simulation.delete(scratch_id)

    report(durations, ENGINE_DAY, args.window)


def copy_of(reference: str) -> Draft:
    """As regras, os jogadores e as estratégias de uma partida salva."""

    if reference.isdigit():
        source = repository.simulation.get_simulation(int(reference))
    else:
        source = next(
            (
                s
                for s in repository.simulation.list_simulations(reference)
                if s.name == reference
            ),
            None,
        )
    if source is None:
        sys.exit("Partida de origem não encontrada.")
    settings = SimulationSettingsDTO.model_validate(
        {
            **source.model_dump(include=set(SimulationSettingsDTO.model_fields)),
            "name": scratch_name(),
        }
    )
    colors = repository.simulation_player.colors(source.id)
    teams = repository.simulation_player.teams(source.id)
    players = []
    for user_id, color in colors.items():
        state = derive_state(repository.strategy.mode_rows(source.id, user_id))
        players.append(
            Player(user_id, color, teams.get(user_id), state.key, state.params or {})
        )
    print(f"Origem: {source.name} (id {source.id}), {len(players)} jogadores")
    return Draft(settings, players)


def recipe(days: int, bots: int) -> Draft:
    """Uma partida clássica de `days` pregões, com `bots` bots de estratégias diferentes."""

    start = backtest_config.coverage().first_date
    if start is None:
        sys.exit("Não há dados de mercado para montar a partida.")
    keys = list(STRATEGIES)
    config = BacktestConfigDTO(
        name=scratch_name(),
        start_date=start,
        end_date=start + timedelta(days=int(days * CALENDAR_PER_TRADING_DAY) + 30),
        starting_cash=STARTING_CASH,
        monthly_contribution=MONTHLY_CONTRIBUTION,
        price_impact=BacktestPriceImpact.REALISTIC,
        participants=[
            BacktestParticipantDTO(
                nickname=f"Bot {n}",
                color=PLAYER_COLORS[n],
                strategy_key=keys[n % len(keys)],
            )
            for n in range(bots)
        ],
    )
    resolved = backtest_config.resolve(config)
    players = [
        Player(0, participant.color, None, bot.strategy_key, bot.params)
        for participant, bot in resolved
    ]
    print(f"Partida de rascunho: {bots} bots a partir de {start:%d/%m/%Y}")
    return Draft(backtest_config.settings_of(config), players)


def scratch_name() -> str:
    return f"{SCRATCH_PREFIX}{datetime.now(UTC):%Y%m%d-%H%M%S}"


def record(
    durations: dict[str, list[float]], kind: str, name: str, duration_ms: float
) -> None:
    if kind == "engine":
        durations[name].append(duration_ms)


@contextmanager
def profile_for(enabled: bool) -> Generator[None]:
    if not enabled:
        yield
        return
    with profiler.capture_engine("profile-match"):
        yield


def run_days(
    sim: Simulation,
    days: int,
    durations: dict[str, list[float]],
    day_name: str,
    checkpoint: int,
) -> None:
    started = time.perf_counter()
    for day in range(1, days + 1):
        day_started = time.perf_counter()
        try:
            sim.next_tick()
        except StopIteration:
            print(f"A partida acabou no dia {day - 1}.")
            break
        # O loop do jogo mede o dia; aqui o script faz o mesmo
        durations[day_name].append((time.perf_counter() - day_started) * 1000)
        if checkpoint and day % checkpoint == 0:
            recent = durations[day_name][-checkpoint:]
            print(
                f"dia {day:>5}: mediana do dia {median_ms(recent):8.1f} ms "
                f"(últimos {len(recent)})"
            )
    print(f"{len(durations[day_name])} dias em {time.perf_counter() - started:.1f} s")


def report(durations: dict[str, list[float]], day_name: str, window: int) -> None:
    """Mediana e p95 de cada etapa nos primeiros e nos últimos `window` dias."""
    days = len(durations[day_name])
    window = min(window, max(1, days // 2))
    print(f"\nPrimeiros {window} dias contra últimos {window} (ms)")
    print(
        f"{'etapa':<28}{'med ini':>9}{'p95 ini':>9}{'med fim':>9}{'p95 fim':>9}{'razão':>7}"
    )
    for name in sorted(durations, key=lambda n: n != day_name):
        values = durations[name]
        # Etapas mensais têm menos medidas que dias: a ponta escala pela contagem
        share = max(1, round(len(values) * window / days))
        first, last = values[:share], values[-share:]
        ratio = median_ms(last) / median_ms(first) if median_ms(first) > 0 else 0.0
        print(
            f"{name:<28}{median_ms(first):9.1f}{p95_ms(first):9.1f}"
            f"{median_ms(last):9.1f}{p95_ms(last):9.1f}{ratio:7.2f}"
        )


if __name__ == "__main__":
    main(sys.argv[1:])
