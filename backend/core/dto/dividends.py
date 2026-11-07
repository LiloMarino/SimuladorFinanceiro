"""Proventos do jogador: o que a Carteira e o detalhe do ativo mostram dos eventos corporativos."""

from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import AssetClass, CorporateEventKind


class DividendPaymentDTO(BaseDTO):
    """Um provento que caiu no caixa do jogador, na data ex."""

    ticker: str
    name: str
    asset_class: AssetClass
    event_date: date
    amount: Decimal


class ClassAmountDTO(BaseDTO):
    asset_class: AssetClass
    amount: Decimal


class PayerAmountDTO(BaseDTO):
    ticker: str
    name: str
    asset_class: AssetClass
    amount: Decimal


class DividendBucketDTO(BaseDTO):
    """Um mês (ou um ano) de proventos, com a divisão por classe e quem pagou."""

    # Primeiro dia do mês, ou 1º de janeiro no ano
    period: date
    amount: Decimal
    by_class: list[ClassAmountDTO]
    # Do que mais pagou ao que menos pagou
    payers: list[PayerAmountDTO]


class DividendPayerDTO(PayerAmountDTO):
    # Fração (0.25 = 25%) dos proventos dos 12 meses que veio deste ativo
    share: Decimal


class PortfolioDividendsDTO(BaseDTO):
    """O card de proventos da Carteira; os 12 meses são os 12 meses-calendário até o da data de hoje."""

    total: Decimal
    total_12m: Decimal
    payments_count: int
    first_payment_date: date | None
    # Recebido em 12 meses ÷ 12: os meses sem provento entram na conta
    average_per_month: Decimal
    # Classes que pagaram na partida, para a legenda
    classes: list[AssetClass]
    monthly: list[DividendBucketDTO]
    yearly: list[DividendBucketDTO]
    payers: list[DividendPayerDTO]


class AssetCorporateEventDTO(BaseDTO):
    """Uma linha do histórico do ativo: um provento, um desdobramento ou um grupamento."""

    ex_date: date
    kind: CorporateEventKind
    # DIVIDEND: valor bruto por ação. SPLIT: a razão (2 é 2 para 1; 0,1 é grupamento 10 para 1)
    value: Decimal
    # Antes da partida o jogador não tinha como receber: os três campos abaixo vêm nulos
    before_match: bool
    # Ações do jogador na abertura da data ex
    shares: Decimal | None
    # Só no desdobramento e no grupamento: as ações depois dele
    shares_after: Decimal | None
    # Provento: o que caiu no caixa. Desdobramento: o valor da fração vendida, se houve
    received: Decimal | None


class AssetCorporateEventsDTO(BaseDTO):
    ticker: str
    asset_class: AssetClass
    # Nulo na cripto, que não paga
    dividend_yield_12m: Decimal | None
    # Provento por ação dos últimos 12 meses, já ajustado aos desdobramentos
    per_share_12m: Decimal
    # Só com posição aberta; nulo sem ela e na cripto
    yield_on_cost: Decimal | None
    received_total: Decimal
    payments_count: int
    match_start_date: date
    # Da data mais recente para a mais antiga, até o dia de hoje da partida
    events: list[AssetCorporateEventDTO]
