from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

from backend.core.dto.base import BaseDTO
from backend.core.dto.government import PROGRAM_NAME_MAX_LENGTH, MeasurePreviewDTO
from backend.core.enum import (
    DividendPolicy,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
    StateMonthReason,
    StateMovementKind,
)

# Fatia do governo em fração: 0,51 é 51% das ações
GovernmentShare = Annotated[Decimal, Field(gt=0, le=1, decimal_places=5)]


class StateOwnedStockRequest(BaseDTO):
    """O que a importação grava ao marcar um ativo como estatal."""

    government_share: GovernmentShare
    shares: Annotated[int, Field(gt=0)]
    # Sem alavanca, a estatal paga dividendo mas não tem preço a segurar
    lever: StateLever | None = None


class StateOwnedStockDTO(StateOwnedStockRequest):
    """A marcação de estatal de um ativo da base."""

    ticker: str


class StateCompanyDTO(BaseDTO):
    """Uma estatal da partida, como a linha de `state_companies` a guarda."""

    id: int
    stock_id: int
    ticker: str
    origin: StateCompanyOrigin
    government_share: Decimal
    shares: int
    lever: StateLever | None
    size: StateCompanySize | None
    invested: Decimal
    mean_return: Decimal | None
    seed: int | None
    status: StateCompanyStatus
    founded_on: date | None
    offer_opened_on: date | None
    privatized_on: date | None
    proceeds: Decimal | None


class StateCompanyMonthDTO(BaseDTO):
    """O mês de uma estatal fundada: valor justo, lucro e o dividendo que foi ao Tesouro."""

    state_company_id: int
    # Primeiro dia do mês
    month: date
    fair_value: Decimal
    profit: Decimal
    treasury_dividend: Decimal


# Painel das estatais


class StateOrderDTO(BaseDTO):
    """A ordem do presidente numa estatal: o degrau do controle de preço e a política de dividendos."""

    control: StateControl
    dividend_policy: DividendPolicy


class StateCompanyRowDTO(BaseDTO):
    """Uma estatal da partida no painel, com o que ela vale e a ordem que recebe."""

    ticker: str
    name: str
    origin: StateCompanyOrigin
    status: StateCompanyStatus
    # Sem alavanca, a estatal paga dividendo mas não tem preço a segurar
    lever: StateLever | None
    size: StateCompanySize | None
    # Fatia do governo em fração: 0,51 é 51% das ações; zero depois da venda
    government_share: Decimal
    shares: int
    # O último preço por ação; None quando a ação ainda não tem preço
    price: Decimal | None
    # O que a fatia do governo vale a esse preço, em reais
    government_value: Decimal
    # O que o governo pagou pela fatia dele na fundação, em reais; None na importada
    invested: Decimal | None
    # O preço por ação que a oferta de privatização usaria hoje: o valor justo na fundada,
    # o preço de mercado na importada; None sem preço ou depois da venda
    fair_price: Decimal | None
    # A última ordem dada, que pode só valer no mês seguinte, e a que vale hoje
    order: StateOrderDTO
    in_force: StateOrderDTO
    # Pontos de IPCA que a ordem em vigor segura
    held_points: Decimal
    # O total que o Tesouro recebeu nos 12 últimos meses fechados (na importada, o provento histórico escalado pela ordem)
    treasury_dividend_12m: Decimal
    # O presidente pode dar ordem agora: a empresa está ativa e sem privatização na fila
    can_command: bool
    # A medida de privatização na fila ou aprovada, quando existe
    privatization_measure_id: int | None
    founded_on: date | None
    privatized_on: date | None
    proceeds: Decimal | None


class StateOfferDTO(BaseDTO):
    """A oferta de privatização aberta: preço, tamanho, o que a sala pediu e o pedido de quem vê."""

    ticker: str
    name: str
    opened_on: date
    # O último pregão da oferta
    ends_on: date
    shares: int
    # O preço por ação da oferta e o que a bolsa cota agora
    price: Decimal | None
    market_price: Decimal | None
    # Ações pedidas por toda a sala; acima de `shares` o rateio é proporcional
    reserved: Decimal
    your_reservation: Decimal | None
    your_cash: Decimal


class StateMovementDTO(BaseDTO):
    """Um fato recente das estatais: fundação, oferta, venda ou mudança de ordem em vigor."""

    day: date
    kind: StateMovementKind
    ticker: str
    # A ordem nova, nos movimentos de ordem
    control: StateControl | None
    dividend_policy: DividendPolicy | None
    # O que a venda rendeu ao Tesouro, em reais
    amount: Decimal | None


class StateSummaryDTO(BaseDTO):
    """O resumo do painel: o que o governo tem nas estatais, o que elas rendem e o que o controle segura."""

    government_value: Decimal
    # Ao Tesouro nos 12 últimos meses fechados, em reais
    treasury_dividends_12m: Decimal
    # A inflação represada hoje, em pontos de nível de preços que voltam na soltura
    backlog_points: Decimal
    # O que as ordens em vigor seguram agora e o teto da soma, em pontos de IPCA
    held_points: Decimal
    cap_points: Decimal


class StateSizeRuleDTO(BaseDTO):
    """Um porte de estatal: o capital que a fundação põe e a dívida que cabe ao governo."""

    size: StateCompanySize
    capital: Decimal
    government_debt: Decimal


class StateLeverRuleDTO(BaseDTO):
    """O peso de uma alavanca: quanto do IPCA e do juro do crédito cada ponto percentual segurado move."""

    lever: StateLever
    ipca_weight: Decimal
    credit_weight: Decimal


class StateRulesDTO(BaseDTO):
    """As regras do jogo que o painel mostra: a fatia da fundação, a janela da oferta, os portes e os pesos."""

    # Fatia do governo na fundação, em fração: 0,51 é 51% das ações
    founding_share: Decimal
    # Pregões que a oferta de privatização fica aberta
    offer_sessions: int
    sizes: list[StateSizeRuleDTO]
    levers: list[StateLeverRuleDTO]


class StateCompaniesPanelDTO(BaseDTO):
    """O painel das estatais: todos leem, e só o presidente comanda."""

    is_president: bool
    rules: StateRulesDTO
    summary: StateSummaryDTO
    companies: list[StateCompanyRowDTO]
    # Do mais novo ao mais antigo
    movements: list[StateMovementDTO]
    offers: list[StateOfferDTO]


class StateStepEffectDTO(BaseDTO):
    """O efeito de um degrau do controle de preço, com a política de hoje."""

    control: StateControl
    percent: int
    held_points: Decimal
    credit_points: Decimal
    # Fração do lucro que o controle tira da empresa
    profit_cut: Decimal
    price_factor: Decimal
    dividend_factor: Decimal
    # O dividendo esperado por mês ao Tesouro; None na fundada sem lucro modelado
    monthly_treasury_dividend: Decimal | None
    # Por que o degrau passa do teto de pontos; None quando está liberado
    blocked_reason: str | None


class StatePolicyEffectDTO(BaseDTO):
    """O efeito de uma política de dividendos, com o controle de hoje."""

    dividend_policy: DividendPolicy
    # Fração do lucro que a política paga ao acionista
    payout: Decimal
    # O preço depois de 4 anos seguidos na política, contra o preço sem ordem
    price_factor: Decimal
    dividend_factor: Decimal
    monthly_treasury_dividend: Decimal | None


class StateOrderPreviewDTO(BaseDTO):
    """O que cada degrau e cada política fariam numa estatal, e o teto que sobra a ela."""

    ticker: str
    name: str
    lever: StateLever | None
    can_command: bool
    order: StateOrderDTO
    cap_points: Decimal
    # O que as outras estatais já seguram e o que fica represado hoje
    other_points: Decimal
    backlog_points: Decimal
    steps: list[StateStepEffectDTO]
    policies: list[StatePolicyEffectDTO]


class FoundStateCompanyRequest(BaseDTO):
    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=1, max_length=PROGRAM_NAME_MAX_LENGTH
        ),
    ]
    ticker: str
    size: StateCompanySize
    lever: StateLever | None = None


class StateFoundingPreviewDTO(BaseDTO):
    """O que fundar a estatal faria: a medida (voto, vigência e dívida) e os efeitos da empresa."""

    measure: MeasurePreviewDTO
    # O capital que a fundação põe na empresa, em reais
    invested: Decimal
    # O gasto primário da fundação por mês, em reais, durante `spending_months` meses
    monthly_spending: Decimal
    spending_months: int
    # O empurrão permanente que a empresa soma ao crescimento, em fração ao ano
    gdp_push: Decimal
    # O dividendo esperado ao Tesouro por ano com a política normal e sem controle, em reais
    expected_treasury_dividend_year: Decimal


class StateOrderRequest(BaseDTO):
    control: StateControl
    dividend_policy: DividendPolicy


class StateReservationRequest(BaseDTO):
    ticker: str
    quantity: Annotated[int, Field(gt=0)]


class StatePolicyPayoutDTO(BaseDTO):
    """Uma política de dividendos e a fração do lucro do mês que ela paga ao acionista."""

    dividend_policy: DividendPolicy
    payout: Decimal


class StateCompanyMonthDetailDTO(BaseDTO):
    """Um mês da estatal fundada na tela da ação, por ação: o que ela fechou e valeu, o que lucrou e o que pagou."""

    # Primeiro dia do mês
    month: date
    reason: StateMonthReason
    # O último fechamento do mês; None sem pregão no mês
    price: Decimal | None
    # O valor justo por ação no fim do mês; None depois da venda
    fair_value: Decimal | None
    # O que o valor justo andou no mês, por ação; None na fundação e depois da venda
    profit: Decimal | None
    # O dividendo pago a cada acionista, por ação; None na fundação e depois da venda
    dividend: Decimal | None
    # A política em vigor no mês e a fração do lucro que ela paga; None na fundação e depois da venda
    dividend_policy: DividendPolicy | None
    payout: Decimal | None


class StateCompanyHoldersDTO(BaseDTO):
    """Quem tem as ações da estatal, em ações; a soma é o total da empresa."""

    government: Decimal
    # O estoque do formador de mercado, que vende a quem compra
    maker: Decimal
    # Os outros jogadores, sem quem vê
    players: Decimal
    bots: Decimal
    funds: Decimal
    you: Decimal


class StateCompanyDetailDTO(BaseDTO):
    """
    A estatal na tela da ação: origem, preço, valor justo, dividendos, política em vigor,
    os meses e quem tem as ações. A importada traz só o preço, o provento dos 12 últimos meses e a política: `months` vem vazia, e `holders`, `fair_value` e `beta`, nulos.
    """

    ticker: str
    origin: StateCompanyOrigin
    status: StateCompanyStatus
    founded_on: date | None
    size: StateCompanySize | None
    # Fatia do governo em fração: 0,51 é 51% das ações; zero depois da venda
    government_share: Decimal
    shares: int
    # O último preço por ação; None sem pregão
    price: Decimal | None
    # O valor justo por ação hoje; None na importada e depois da venda
    fair_value: Decimal | None
    # O dividendo por ação: o somado desde a fundação na fundada e o dos 12 meses fechados na importada
    dividends: Decimal
    # A política de dividendos em vigor hoje
    dividend_policy: DividendPolicy
    # As políticas que o presidente pode escolher, cada uma com o payout dela
    policies: list[StatePolicyPayoutDTO]
    # Quanto da bolsa a ação acompanha (0,8 é 80% do retorno do Ibovespa da partida); None na importada
    beta: Decimal | None
    # Do mais antigo ao mais novo: a fundação, cada mês fechado e a venda
    months: list[StateCompanyMonthDetailDTO]
    holders: StateCompanyHoldersDTO | None
