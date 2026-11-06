"""O Tesouro Direto como a tela mostra: catálogo, histórico, termômetro, posições e venda."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from backend.core.dto.base import BaseDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import RateIndexType


class TreasuryTitleDTO(BaseDTO):
    """Um título do catálogo no mês: a taxa travada de quem compra hoje, aberta em base e prêmio."""

    asset_uuid: UUID
    name: str
    rate_index: RateIndexType
    maturity_date: date
    months_to_maturity: int
    # Frações ao ano; `rate` é `base_rate + premium` e é o que fica travado na compra
    base_rate: Decimal
    premium: Decimal
    rate: Decimal
    # O que o título rende ao ano hoje; None quando a partida esconde a taxa equivalente
    effective_annual_rate: Decimal | None
    # 31 de dezembro do ano em que o título sai da vitrine
    sold_until: date
    # O título que entra no lugar quando a saída é no fechamento de dezembro deste ano
    replacement_name: str | None


class TreasuryThermometerDTO(BaseDTO):
    """O risco do país que decide o prêmio; só existe com a expansão Governo & Política."""

    # Fração ao ano (0.0234 = 2,34 pontos), somada à taxa de todos os títulos
    premium: Decimal
    # Quanto o próximo ponto percentual de dívida soma ao prêmio, em fração ao ano
    premium_per_debt_point: Decimal
    band: str
    band_index: int
    # Dívida ÷ PIB em fração (0.887 = 88,7%) e sua variação nos últimos 12 meses (None antes de 12 meses)
    debt: Decimal
    debt_change_12m: Decimal | None
    # None na faixa mais alta
    next_band: str | None
    next_band_limit: Decimal | None
    # Quanto falta de dívida ÷ PIB para a próxima faixa, em fração
    debt_to_next_band: Decimal | None
    # Meses até a próxima faixa no ritmo dos últimos 12 meses; None se a dívida não sobe
    months_to_next_band: int | None


class TreasuryCatalogDTO(BaseDTO):
    # A taxa vale até o dia anterior: no dia 1º do mês seguinte ela é revista
    next_review: date
    titles: list[TreasuryTitleDTO]
    thermometer: TreasuryThermometerDTO | None


class TreasuryHistoryQuoteDTO(BaseDTO):
    name: str
    rate_index: RateIndexType
    maturity_date: date
    base_rate: Decimal
    premium: Decimal
    effective_annual_rate: Decimal | None


class TreasuryHistoryPointDTO(BaseDTO):
    """Um mês do gráfico: as cotações do catálogo e, com o governo, o prêmio e a dívida ÷ PIB."""

    month: date
    selic: Decimal
    ipca: Decimal
    premium: Decimal
    debt: Decimal | None
    band_index: int | None
    quotes: list[TreasuryHistoryQuoteDTO]


class TreasuryPositionDTO(BaseDTO):
    """Uma posição do jogador no Tesouro, com o que ela rendeu e o que o mercado faz com ela."""

    asset: FixedIncomeAssetDTO
    first_applied_date: date
    # A taxa travada na compra e a que o mesmo título paga hoje
    bought_rate: Decimal
    today_rate: Decimal
    total_applied: Decimal
    # O que a curva rendeu sobre o aplicado
    yield_amount: Decimal
    # Preço de hoje menos a curva; zero na Selic
    mark: Decimal
    market_value: Decimal


class TreasurySaleQuoteDTO(BaseDTO):
    """
    A venda de `amount` bruto do título hoje, a mercado. Os campos de valor são None quando
    `amount` é zero ou passa de `max_amount`, o valor de mercado da posição inteira.
    """

    amount: Decimal
    max_amount: Decimal
    first_applied_date: date
    bought_rate: Decimal
    today_rate: Decimal
    days_held: int
    # A parte vendida: aplicado, rendimento da curva e marcação
    applied_amount: Decimal | None
    yield_amount: Decimal | None
    mark: Decimal | None
    iof_rate: Decimal
    iof: Decimal | None
    income_tax_rate: Decimal
    income_tax: Decimal | None
    net_amount: Decimal | None
    cash_before: Decimal
    cash_after: Decimal | None
    remaining: Decimal | None
    full: bool
    # Esperar a mesma parte até o vencimento, sem marcação
    maturity_date: date
    maturity_gross_amount: Decimal | None
    maturity_income_tax: Decimal | None
    maturity_net_amount: Decimal | None


class TreasuryCoverDTO(BaseDTO):
    """A opção de a cobertura automática vender também Prefixado e IPCA+, a mercado."""

    enabled: bool
