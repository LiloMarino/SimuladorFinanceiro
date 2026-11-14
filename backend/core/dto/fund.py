from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO

# Quatro letras e o 11 das cotas
FUND_TICKER_PATTERN = r"^[A-Z]{4}11$"
FundTicker = Annotated[str, StringConstraints(pattern=FUND_TICKER_PATTERN)]
FundName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=40)
]
# Taxa ao ano em fração: 0,02 é 2%
FeeRate = Annotated[Decimal, Field(ge=0, le=1, decimal_places=4)]


class FundTermsDTO(BaseDTO):
    """O que a gestora mostra a quem a vê: cotas, oferta, taxas e marca d'água."""

    id: int
    ticker: str
    founder_user_id: int
    manager_user_id: int
    name: str
    quotas: Decimal
    maker_quotas: Decimal
    offer_remaining: Decimal | None
    listed_on: date | None
    # As cotas postas à venda e o preço da oferta, fixados na abertura
    offer_quotas: Decimal | None
    offer_price: Decimal | None
    # O dia em que a oferta fechou; nulo com a oferta aberta ou sem oferta
    offer_closed_on: date | None
    management_fee: Decimal
    performance_fee: Decimal
    pending_management_fee: Decimal | None
    pending_performance_fee: Decimal | None
    pending_from: date | None
    high_water_mark: Decimal | None
    high_water_mark_on: date | None
    last_performance_on: date | None


class FundDTO(FundTermsDTO):
    """Uma gestora da partida, como a linha de `funds` a guarda."""

    stock_id: int
    portfolio_id: int
    client_id: uuid.UUID
    maker_cash: Decimal


class FundOfferSaleDTO(BaseDTO):
    """Uma venda da oferta pública; sem comprador quando quem levou as cotas foi o formador de mercado."""

    day: date
    buyer_user_id: int | None
    quotas: Decimal
    price: Decimal


class FundDayDTO(BaseDTO):
    """O fechamento de uma gestora num pregão."""

    day: date
    nav: Decimal
    quotas: Decimal
    traded_quantity: Decimal
    traded_value: Decimal
    ranking_price: Decimal


class FundSummaryDTO(FundTermsDTO):
    """A gestora na lista da partida, com o PL por cota de agora e o preço de ranking."""

    nav: Decimal | None
    ranking_price: Decimal | None
    # O preço do último negócio da cota; nulo enquanto ela nunca negociou. O ágio é preço / nav - 1
    price: Decimal | None
    manager_nickname: str | None
    # O pregão da oferta pública (1 a 5) e o dia em que ela fecha sozinha; nulos sem oferta aberta
    offer_session: int | None
    offer_ends_on: date | None
    # O último dia do mandato do gestor presidente, em que a gestora fica congelada; nulo se opera
    frozen_until: date | None


# Quem tem cotas: jogador, bot ou o formador de mercado
type FundHolderKind = Literal["player", "bot", "maker"]
# As classes em que a gestora mantém patrimônio: o Tesouro à parte da renda fixa de crédito
type FundHoldingClass = Literal["cash", "stocks", "fixed_income", "treasury"]
type FundMovementType = Literal[
    "contribution",
    "offer_opened",
    "offer_closed",
    "management_fee",
    "performance_fee",
    "report_published",
    "manager_buy",
    "manager_sell",
]


class FundHolderDTO(BaseDTO):
    kind: FundHolderKind
    # Nulo no formador de mercado
    user_id: int | None
    nickname: str
    color: str | None
    quotas: Decimal
    # Fração das cotas em circulação: 0,25 é 25%
    share: Decimal


class FundCompositionDTO(BaseDTO):
    """O patrimônio da gestora numa classe, hoje."""

    asset_class: FundHoldingClass
    value: Decimal
    # Fração do patrimônio: 0,40 é 40%
    fraction: Decimal


class FundPositionDTO(BaseDTO):
    """Uma posição da gestora: o caixa, uma ação (com quantidade) ou um título de renda fixa."""

    ticker: str | None
    name: str
    asset_class: FundHoldingClass
    quantity: Decimal | None
    value: Decimal
    fraction: Decimal


class FundReportDTO(BaseDTO):
    """O relatório mensal: as posições no último pregão do mês fechado."""

    day: date
    positions: list[FundPositionDTO]


class FundSeriesPointDTO(BaseDTO):
    day: date
    # O fechamento do pregão; nulo antes da primeira vela
    close: Decimal | None
    nav: Decimal


class FundFeesDTO(BaseDTO):
    management_fee: Decimal
    # O que a administração cobra no próximo mês: taxa anual / 12 x PL por cota x cotas fora do formador
    management_monthly_estimate: Decimal
    performance_fee: Decimal
    # O que a performance cobraria se o semestre fechasse hoje, pela marca d'água; nulo antes da oferta
    performance_estimate: Decimal | None
    next_performance_on: date | None
    high_water_mark: Decimal | None
    high_water_mark_on: date | None
    # O que o gestor recebeu de taxas (administração e performance) nos últimos 12 meses
    received_12m: Decimal


class FundMovementDTO(BaseDTO):
    day: date
    type: FundMovementType
    quotas: Decimal | None
    price: Decimal | None
    # Valor em reais do movimento
    amount: Decimal | None
    ticker: str | None


class FundOfferBuyerDTO(BaseDTO):
    """Quem comprou na oferta em andamento; os bots entram somados numa linha só."""

    kind: FundHolderKind
    user_id: int | None
    nickname: str
    color: str | None
    quotas: Decimal


class FundDetailsDTO(FundSummaryDTO):
    """A página da gestora: quem tem as cotas, a carteira, o desempenho, as taxas e a oferta."""

    holders: list[FundHolderDTO]
    # Cotas que dão o controle: mais da metade das cotas em circulação
    control_quotas: Decimal
    # Quanto o gestor vende sem perder o controle; só o gestor vê
    sellable_keeping_control: Decimal | None
    composition: list[FundCompositionDTO]
    # Rentabilidade do PL por cota nos últimos 12 meses e o CDI do mesmo período (0,10 é 10%);
    # numa gestora mais nova que isso valem desde `return_since`
    return_12m: Decimal | None
    return_since: date | None
    cdi_12m: Decimal | None
    series: list[FundSeriesPointDTO]
    last_report: FundReportDTO | None
    fees: FundFeesDTO
    # Os movimentos mais novos primeiro
    movements: list[FundMovementDTO]
    # A oferta em andamento: cotas vendidas, o que entrou no caixa e quem comprou; nulos sem oferta aberta
    offer_sold: Decimal | None
    offer_raised: Decimal | None
    offer_buyers: list[FundOfferBuyerDTO] | None
    # A carteira posição a posição, ao vivo; só o gestor vê
    positions: list[FundPositionDTO] | None
    # As cotas de quem consulta, ao preço de ranking (o do patrimônio no ranking), e o retorno
    # sobre o custo médio dele; nulo sem cotas
    my_quotas: Decimal
    my_value: Decimal
    my_return: Decimal | None


class FundAccountDTO(BaseDTO):
    """Uma conta com que o jogador opera: a pessoal (sem gestora) ou uma gestora que ele gere."""

    fund_id: int | None
    name: str
    ticker: str | None
    cash: Decimal
    frozen_until: date | None


class FundTickerCheckDTO(BaseDTO):
    """O que a conferência da sigla achou: livre, fora do formato, de um ativo ou de uma gestora."""

    ticker: str
    status: Literal["free", "format", "asset", "fund"]
    owner_name: str | None


class FundFoundRequest(BaseDTO):
    name: FundName
    ticker: FundTicker
    management_fee: FeeRate
    performance_fee: FeeRate


class FundContributionStockRequest(BaseDTO):
    ticker: str
    quantity: Decimal = Field(gt=0, decimal_places=8)


class FundContributionRequest(BaseDTO):
    cash: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    stocks: list[FundContributionStockRequest] = Field(default_factory=list)


class FundContributionResponse(BaseDTO):
    quotas: Decimal


class FundOfferRequest(BaseDTO):
    quotas: int = Field(gt=0)


class FundFeesRequest(BaseDTO):
    management_fee: FeeRate
    performance_fee: FeeRate
