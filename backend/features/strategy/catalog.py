"""
O que as estratégias oferecem antes de haver motor: a lista com os padrões da
data, os parâmetros completos e a validação. A sala (bots no lobby) e a partida
(automático do jogador) leem o mesmo catálogo.
"""

from __future__ import annotations

from collections.abc import Collection
from datetime import date

from backend.core import repository
from backend.core.dto.strategy import (
    StrategyInfoDTO,
    StrategyParamDTO,
    StrategyParamValue,
)
from backend.core.enum import StrategyParamKind
from backend.features.strategy.base_strategy import BaseStrategy, ParamSpec
from backend.features.strategy.registry import STRATEGIES

# Ações padrão: as de maior volume financeiro médio nos últimos pregões, ao ligar
DEFAULT_TICKER_COUNT = 10
DEFAULT_TICKER_SESSIONS = 60


def known_tickers() -> set[str]:
    """Todas as ações cadastradas, as mesmas que o motor da partida conhece."""
    return {stock.ticker for stock in repository.stock.get_stocks()}


def infos(
    today: date, simulation_id: int | None, known: Collection[str]
) -> list[StrategyInfoDTO]:
    """As estratégias do app, com os padrões calculados para `today`."""
    tickers = default_tickers(today, simulation_id)
    return [
        StrategyInfoDTO(
            key=cls.key,
            name=cls.name,
            bot_names=list(cls.bot_names),
            summary=cls.summary,
            description=cls.description,
            group=cls.group,
            view=cls.view_kind,
            term_hint=cls.term_hint,
            params=[
                param_dto(spec, tickers, today, simulation_id, known)
                for spec in cls.params
            ],
        )
        for cls in STRATEGIES.values()
    ]


def with_defaults(
    cls: type[BaseStrategy],
    params: dict[str, StrategyParamValue],
    today: date,
    simulation_id: int | None,
    known: Collection[str],
) -> dict[str, StrategyParamValue]:
    """Os parâmetros da estratégia, com o padrão no lugar do que faltou."""
    resolved: dict[str, StrategyParamValue] = {}
    for spec in cls.params:
        if spec.key in params:
            resolved[spec.key] = params[spec.key]
        elif spec.kind is StrategyParamKind.TICKERS:
            resolved[spec.key] = default_tickers(today, simulation_id)
        elif spec.kind is StrategyParamKind.TICKER:
            resolved[spec.key] = default_asset(spec, today, simulation_id, known)
        elif spec.default is not None:
            resolved[spec.key] = spec.default
    return resolved


def default_tickers(today: date, simulation_id: int | None) -> list[str]:
    return repository.stock.get_most_traded(
        today, DEFAULT_TICKER_SESSIONS, DEFAULT_TICKER_COUNT, simulation_id
    )


def default_asset(
    spec: ParamSpec, today: date, simulation_id: int | None, known: Collection[str]
) -> str:
    """O ativo preferido do parâmetro; sem ele na partida, a ação mais negociada."""
    if isinstance(spec.default, str) and spec.default in known:
        return spec.default
    most_traded = default_tickers(today, simulation_id)
    return most_traded[0] if most_traded else str(spec.default)


def param_dto(
    spec: ParamSpec,
    tickers: list[str],
    today: date,
    simulation_id: int | None,
    known: Collection[str],
) -> StrategyParamDTO:
    hint = spec.hint
    default: StrategyParamValue
    if spec.kind is StrategyParamKind.TICKERS:
        default = tickers
    elif spec.kind is StrategyParamKind.TICKER:
        default = default_asset(spec, today, simulation_id, known)
        if default != spec.default:
            hint += f" Esta partida não tem o {spec.default}: o padrão é {default}."
    else:
        default = spec.default or 0
    return StrategyParamDTO(
        key=spec.key,
        label=spec.label,
        kind=spec.kind,
        default=default,
        min=spec.min,
        max=spec.max,
        unit=spec.unit,
        hint=hint,
    )
