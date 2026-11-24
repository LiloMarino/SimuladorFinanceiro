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
from backend.core.professions import Expansion
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
    default: bool | int | str | None = None
    min: int | None = None
    max: int | None = None
    unit: str | None = None
    # A chave (boolean) que precisa estar ligada para este parâmetro valer
    enabled_by: str | None = None


# Os dois parâmetros que toda estratégia com `supports_leverage` recebe da base
LEVERAGE_KEY = "leverage"
TARGET_DEBT_KEY = "target_debt"
LEVERAGE_PARAMS = (
    ParamSpec(
        key=LEVERAGE_KEY,
        label="Alavancar",
        kind=StrategyParamKind.BOOLEAN,
        default=False,
        hint=(
            "Liga o crédito: com o Ibovespa acima da média dos últimos 200 pregões, o "
            "automático toma empréstimo até a dívida-alvo e investe esse dinheiro; "
            "quando o Ibovespa cai abaixo da média, vende ações, quita a dívida e volta "
            "a investir só o patrimônio. Alavancar amplia ganhos e perdas, e o juro do "
            "empréstimo entra na conta: com patrimônio de R$ 100.000 e dívida de "
            "R$ 20.000, uma queda de 10% na carteira (R$ 120.000) tira R$ 12.000, e o "
            "patrimônio cai 12%, para R$ 88.000."
        ),
    ),
    ParamSpec(
        key=TARGET_DEBT_KEY,
        label="Dívida-alvo",
        kind=StrategyParamKind.PERCENT,
        default=20,
        min=5,
        max=50,
        unit="%",
        enabled_by=LEVERAGE_KEY,
        hint=(
            "A dívida que o automático mantém, em % do patrimônio líquido (o que você "
            "tem menos o que deve). Com patrimônio de R$ 100.000 e 20%, a dívida chega "
            "a R$ 20.000. O limite da sua nota de crédito também vale: o automático "
            "nunca passa dele."
        ),
    ),
)


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
    # Nomes sugeridos para o bot que joga esta estratégia
    bot_names: ClassVar[tuple[str, ...]] = ()
    # A expansão da partida que a estratégia exige; nulo é a que toda sala tem
    requires_expansion: ClassVar[Expansion | None] = None
    # Se a estratégia também opera a carteira de uma gestora; a gestora não compra cota de outras gestoras
    fund_account: ClassVar[bool] = True
    # Se a estratégia aceita alavancar com crédito: a base acrescenta "Alavancar" e "Dívida-alvo" aos parâmetros
    supports_leverage: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        own = {spec.key for spec in cls.params}
        if cls.supports_leverage and LEVERAGE_KEY not in own:
            cls.params = (*cls.params, *LEVERAGE_PARAMS)

    @classmethod
    def available(cls, *, funds_enabled: bool, government_enabled: bool) -> bool:
        """Se a sala tem a expansão que a estratégia exige."""
        expansions = {
            Expansion.FUNDS: funds_enabled,
            Expansion.GOVERNMENT: government_enabled,
        }
        return cls.requires_expansion is None or expansions.get(
            cls.requires_expansion, False
        )

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
            elif spec.kind is StrategyParamKind.BOOLEAN:
                message = _boolean_error(spec, value)
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
    if not isinstance(value, int):
        raise TypeError(f"O parâmetro {key} precisa ser inteiro")
    return value


def param_bool(params: dict[str, StrategyParamValue], key: str) -> bool:
    """A chave liga/desliga; a ausente (parâmetros gravados antes dela existir) é desligada."""
    return params.get(key) is True


def param_ticker(params: dict[str, StrategyParamValue], key: str) -> str:
    value = params[key]
    if not isinstance(value, str):
        raise TypeError(f"O parâmetro {key} precisa ser texto")
    return value


def param_tickers(params: dict[str, StrategyParamValue], key: str) -> list[str]:
    value = params[key]
    if not isinstance(value, list):
        raise TypeError(f"O parâmetro {key} precisa ser lista")
    return value


def _boolean_error(spec: ParamSpec, value: StrategyParamValue | None) -> str | None:
    if not isinstance(value, bool):
        return f"{spec.label} precisa ser ligado ou desligado."
    return None


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
