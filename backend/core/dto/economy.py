from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import EconomyLink, EffectPhase, MeasureKind


class EconomyPointDTO(BaseDTO):
    """A economia num dia da partida; as taxas são frações (0.1425 = 14,25% ao ano)."""

    date: date
    selic: Decimal
    # Inflação acumulada em 12 meses
    ipca: Decimal
    # SELIC menos IPCA: quanto o dinheiro rende de verdade
    real_rate: Decimal
    # Meta de inflação do ano
    target: Decimal
    # Folga da meta: a inflação dentro de meta ± tolerância cumpre o regime de metas
    tolerance: Decimal
    # Crescimento do PIB em 12 meses e desemprego, no último fechamento de mês
    growth: Decimal
    unemployment: Decimal
    # Dívida bruta em fração do PIB e prêmio de risco que ela cobra; nulos sem a expansão Governo
    debt: Decimal | None
    premium: Decimal | None
    # O Ibovespa (pontos) da partida; nulo quando a série não cobre o dia
    ibovespa: Decimal | None
    # A SELIC, o IPCA e o Ibovespa da série guardada, sem as medidas de gasto; nulos sem a expansão Governo
    stored_selic: Decimal | None
    stored_ipca: Decimal | None
    stored_ibovespa: Decimal | None


class CopomChangeDTO(BaseDTO):
    """Dia em que a SELIC mudou de nível."""

    date: date
    # A mudança em fração (0.005 = sobe 0,5 ponto)
    change: Decimal
    # A SELIC depois da mudança
    selic: Decimal


class GrowthPartsDTO(BaseDTO):
    """
    O crescimento do PIB em 12 meses e o desemprego no último fechamento de mês, em
    fração: o da história mais o que a partida somou. A história é a série do IBGE, ou o
    modelo onde ela não cobre.
    """

    history_growth: Decimal
    # O que a partida soma ao crescimento, por causa: o juro real e a bolsa diferentes da
    # história, as obras e o impulso fiscal (o primário que piorou em 12 meses)
    real_rate: Decimal
    stocks: Decimal
    works: Decimal
    impulse: Decimal
    growth: Decimal
    history_unemployment: Decimal
    unemployment: Decimal


class DebtCausesDTO(BaseDTO):
    """
    A variação da dívida nos últimos meses fechados, em fração do PIB, por causa: o juro
    a aumenta, o crescimento e a inflação a encolhem (aumentam o PIB) e o primário a
    abate ou a aumenta. A soma das quatro é a variação inteira.
    """

    months: int
    interest: Decimal
    growth: Decimal
    inflation: Decimal
    primary: Decimal


class DebtSummaryDTO(BaseDTO):
    """A dívida do governo no último fechamento de mês."""

    month_end: date
    # Em fração do PIB
    debt: Decimal
    premium: Decimal
    # A dívida da história: a política padrão de impostos e o gasto base
    history_debt: Decimal
    # A taxa média que a dívida paga ao ano: parte na SELIC do dia, parte no que os
    # títulos dos últimos 36 meses travaram
    rate: Decimal
    causes: DebtCausesDTO
    # Em reais: a dívida, o PIB em 12 meses e o resultado do mês (negativo é déficit); o
    # resultado é nulo antes do primeiro fechamento
    debt_amount: Decimal
    gdp: Decimal
    month_result: Decimal | None


class ActiveEffectDTO(BaseDTO):
    """O efeito de uma medida de gasto aprovada na economia da partida, hoje."""

    measure_id: int
    kind: MeasureKind
    title: str
    # O valor depois da medida e o de antes: fração do PIB ao ano ou ganho real ao ano
    value: Decimal
    before: Decimal
    # O dia em que a medida passou a valer, o dia em que o efeito chega cheio e o dia em que já não pesa
    effective: date
    peak_on: date
    faded_on: date
    phase: EffectPhase
    # Pontos de IPCA e de SELIC que a medida põe hoje e a variação da bolsa (fração) no trimestre
    inflation: Decimal
    selic: Decimal
    stocks: Decimal
    # Pontos de IPCA mês a mês desde a vigência e quantos meses já correram
    curve: list[Decimal]
    elapsed_months: int


class LinkEffectDTO(BaseDTO):
    """Uma ligação da economia interligada hoje: o desvio do último mês fechado e o que ele soma."""

    link: EconomyLink
    # O desvio da partida contra a história, em fração: o desemprego, o prêmio de risco ou o nível do PIB
    gap: Decimal
    # Pontos de IPCA e de SELIC em 12 meses e a variação da bolsa (fração) no trimestre
    inflation: Decimal
    selic: Decimal
    stocks: Decimal


class EconomyPanelDTO(BaseDTO):
    points: list[EconomyPointDTO]
    copom_changes: list[CopomChangeDTO]
    growth_parts: GrowthPartsDTO
    # Só nas partidas com a expansão Governo & Política
    debt: DebtSummaryDTO | None
    # Os efeitos das medidas de gasto aprovadas e das ligações; nulos sem a expansão Governo
    effects: list[ActiveEffectDTO] | None
    links: list[LinkEffectDTO] | None
