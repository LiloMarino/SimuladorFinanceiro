from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

import pandas as pd

from backend.core.dto.strategy import (
    AllocationViewDTO,
    RankingViewDTO,
    SignalLevelDTO,
    SignalLineDTO,
    SignalMarkerDTO,
    StrategyParamValue,
)
from backend.core.enum import StrategyGroup, StrategyParamKind, StrategyView
from backend.features.strategy.context import StrategyContext

# Ações que uma estratégia pode operar de uma vez
MAX_TICKERS = 30
# Pregões desenhados no gráfico do sinal (cerca de um ano)
CHART_DAYS = 252


@dataclass(frozen=True)
class ParamSpec:
    """Um parâmetro que o jogador ajusta: o que é, a faixa que vale e o padrão."""

    key: str
    label: str
    kind: StrategyParamKind
    hint: str
    # Nulo no padrão de `tickers`, que é calculado para a partida ao ligar. Em
    # `ticker` é o ativo preferido, que cede à ação mais negociada quando a
    # partida não o tem.
    default: int | str | None = None
    min: int | None = None
    max: int | None = None
    unit: str | None = None


@dataclass(frozen=True)
class Signal:
    """O que a estratégia olha num ativo e onde ela compraria e venderia."""

    lines: list[SignalLineDTO]
    markers: list[SignalMarkerDTO]
    # Linhas horizontais do painel do oscilador
    levels: list[SignalLevelDTO] = field(default_factory=list)


class BaseStrategy:
    """
    Estratégia do app: uma classe sem estado, que a cada dia lê o contexto do
    jogador e enfileira intenções. Bot, automático e backtest usam esta mesma interface.

    Responsável por:
    - Declarar nome, descrição, grupo e parâmetros (com faixa e padrão)
    - Validar os parâmetros em português, campo a campo
    - Decidir o dia em `next` e desenhar o que olha em `signal` ou em `view`
    """

    key: ClassVar[str]
    name: ClassVar[str]
    summary: ClassVar[str]
    description: ClassVar[str]
    group: ClassVar[StrategyGroup]
    params: ClassVar[tuple[ParamSpec, ...]] = ()
    # O bloco do detalhe: `signal` desenha o gráfico de um ativo; `view` monta o
    # ranking ou a alocação a partir da carteira do jogador
    view_kind: ClassVar[StrategyView] = StrategyView.NONE
    # Explicação do termo técnico que a regra usa
    term_hint: ClassVar[str | None] = None

    @classmethod
    def validate(
        cls, params: dict[str, StrategyParamValue], known_tickers: set[str]
    ) -> dict[str, str]:
        """Erros por campo; vazio quando os parâmetros valem."""
        errors: dict[str, str] = {}
        for spec in cls.params:
            value = params.get(spec.key)
            if spec.kind is StrategyParamKind.TICKERS:
                message = _tickers_error(spec, value, known_tickers)
            elif spec.kind is StrategyParamKind.TICKER:
                message = _ticker_error(spec, value, known_tickers)
            else:
                message = _number_error(spec, value)
            if message:
                errors[spec.key] = message
        return errors

    @classmethod
    def needed_days(cls, params: dict[str, StrategyParamValue]) -> int:
        """Pregões de histórico que a estratégia pede para ter sinal."""
        return 0

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        """Decide o dia: enfileira intenções no contexto."""

    def signal(
        self, history: pd.DataFrame, params: dict[str, StrategyParamValue]
    ) -> Signal | None:
        """As linhas e os marcadores do ativo; nulo quando o histórico não basta."""
        return None

    def view(
        self, ctx: StrategyContext, params: dict[str, StrategyParamValue]
    ) -> RankingViewDTO | AllocationViewDTO | None:
        """O ranking ou a alocação do jogador hoje."""
        return None


def param_int(params: dict[str, StrategyParamValue], key: str) -> int:
    value = params[key]
    assert isinstance(value, int)
    return value


def param_ticker(params: dict[str, StrategyParamValue], key: str) -> str:
    value = params[key]
    assert isinstance(value, str)
    return value


def param_tickers(params: dict[str, StrategyParamValue], key: str) -> list[str]:
    value = params[key]
    assert isinstance(value, list)
    return value


def _number_error(spec: ParamSpec, value: StrategyParamValue | None) -> str | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return f"{spec.label} precisa ser um número inteiro."
    if spec.min is not None and value < spec.min:
        return f"{spec.label} precisa ser de {spec.min} a {spec.max}{_unit(spec)}."
    if spec.max is not None and value > spec.max:
        return f"{spec.label} precisa ser de {spec.min} a {spec.max}{_unit(spec)}."
    return None


def _unit(spec: ParamSpec) -> str:
    if spec.unit is None:
        return ""
    return spec.unit if spec.unit == "%" else f" {spec.unit}"


def _ticker_error(
    spec: ParamSpec, value: StrategyParamValue | None, known: set[str]
) -> str | None:
    if not isinstance(value, str) or value not in known:
        return f"Escolha uma ação da partida em {spec.label.lower()}."
    return None


def _tickers_error(
    spec: ParamSpec, value: StrategyParamValue | None, known: set[str]
) -> str | None:
    if not isinstance(value, list) or not all(isinstance(t, str) for t in value):
        return f"{spec.label} precisa ser uma lista de tickers."
    if not value:
        return f"Escolha ao menos uma ação em {spec.label.lower()}."
    if len(value) > MAX_TICKERS:
        return f"{spec.label} aceita até {MAX_TICKERS} ações."
    unknown = sorted(set(value) - known)
    if unknown:
        return f"Ação desconhecida em {spec.label.lower()}: {', '.join(unknown)}."
    return None
