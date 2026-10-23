"""Contratos e regras versionadas da expansão de governo."""

import math
from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator

from backend.core.dto.base import BaseDTO
from backend.core.dto.portfolio import PortfolioDTO

PolicyKind = Literal[
    "COMMON_TAX",
    "DAY_TRADE_TAX",
    "FII_TAX",
    "STOCK_EXEMPTION",
    "FIXED_TAX_SHIFT",
    "LCI_TAX",
    "SECTOR_TAX",
    "PRODUCT_TARIFF",
    "PUBLIC_SPENDING",
]


class GovernmentDTO(BaseDTO):
    model_config = ConfigDict(frozen=False, extra="forbid", from_attributes=True)


class ProductExposureDTO(GovernmentDTO):
    product: Literal["STEEL", "OIL", "FOOD", "TECH"]
    revenue_share: float = Field(ge=0, le=1)
    imported_cost_share: float = Field(ge=0, le=1)
    domestic_competition: float = Field(default=0.3, ge=0, le=1)
    pass_through: float = Field(default=0.4, ge=0, le=1)


class CompanyProfileDTO(GovernmentDTO):
    ticker: str
    sector: str | None = None
    segment: str | None = None
    margin: float = Field(default=0.15, ge=0.02, le=0.8)
    beta: float = Field(default=1, ge=0, le=3)
    exposures: list[ProductExposureDTO] = Field(default_factory=list)
    source: str = "Hipótese do cenário; não representa dados financeiros da empresa"


class ElectorateDTO(GovernmentDTO):
    name: str = Field(min_length=2, max_length=60)
    weight: float = Field(gt=0, le=1)
    position: float = Field(ge=1, le=5)
    campaign_sensitivity: float = Field(default=1, ge=0, le=2)


def default_electorate() -> list[ElectorateDTO]:
    return [
        ElectorateDTO(name="Investidores", weight=0.25, position=1.5),
        ElectorateDTO(name="Empreendedores", weight=0.30, position=2.5),
        ElectorateDTO(name="Serviços públicos", weight=0.30, position=4.5),
        ElectorateDTO(
            name="Equilíbrio fiscal", weight=0.15, position=3, campaign_sensitivity=0.7
        ),
    ]


class GovernmentRulesDTO(GovernmentDTO):
    enabled: bool = False
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    ranking: Literal["individual", "parties"] = "individual"
    manual_selic: bool = False
    model_version: Literal["government-v1"] = "government-v1"
    impeachment_floor: float = Field(default=25, ge=5, le=40)
    impeachment_months: int = Field(default=3, ge=2, le=12)
    campaign_scale: Decimal = Field(default=Decimal(8000), gt=0, le=Decimal(1000000))
    inflation_target: float = Field(default=0.03, ge=0, le=0.10)
    initial_treasury: Decimal = Field(
        default=Decimal(1000000000), ge=0, le=Decimal(1000000000000)
    )
    # Regras de jogo explícitas, não coeficientes estimados de uma economia real.
    spending_inflation: float = Field(default=0.01, ge=0, le=0.05)
    monetary_inflation: float = Field(default=0.25, ge=0, le=1)
    electorate: list[ElectorateDTO] = Field(
        default_factory=default_electorate, min_length=1, max_length=12
    )
    companies: list[CompanyProfileDTO] = Field(default_factory=list, max_length=500)

    @model_validator(mode="after")
    def unique_profiles(self):
        if not math.isclose(sum(g.weight for g in self.electorate), 1, abs_tol=1e-9):
            raise ValueError("Os pesos dos perfis de eleitores precisam somar 100%.")
        if len({g.name for g in self.electorate}) != len(self.electorate):
            raise ValueError("Os perfis de eleitores precisam de nomes diferentes.")
        if len({c.ticker for c in self.companies}) != len(self.companies):
            raise ValueError("Cada ativo pode ter apenas um perfil empresarial.")
        for company in self.companies:
            if len({e.product for e in company.exposures}) != len(company.exposures):
                raise ValueError("Cada produto aparece uma vez por empresa.")
        return self


class PartyDTO(GovernmentDTO):
    id: int
    name: str
    acronym: str
    color: str
    founder: int | None
    members: list[int] = Field(default_factory=list)
    contributions: dict[str, Decimal] = Field(default_factory=dict)
    candidate: int | None = None
    candidate_name: str | None = None
    candidate_accepted: bool = False
    vice: int | None = None
    vice_accepted: bool = False
    promise: float = 3
    spent: Decimal = Decimal(0)
    support: float = 0
    is_ai: bool = False
    campaign_active: bool = True


class PolicyDTO(GovernmentDTO):
    id: int
    kind: PolicyKind
    target: str = ""
    value: Decimal
    proposed_on: date
    author: int
    party_id: int
    status: Literal["queued", "approved", "rejected", "withdrawn"] = "queued"
    voted_on: date | None = None
    effective_on: date | None = None
    position: float


class ElectionResultDTO(GovernmentDTO):
    year: int
    round: int
    on: date
    votes: dict[str, float]
    finalists: list[int]
    winner: int | None = None
    by_profile: dict[str, dict[str, float]] = Field(default_factory=dict)


class TermDTO(GovernmentDTO):
    party_id: int
    president: int
    vice: int | None = None
    start: date
    end: date
    approval: float = 50
    low_months: int = 0
    neutral: bool = False


class SelicDecisionDTO(GovernmentDTO):
    on: date
    rate: float
    baseline: float


class GovernmentStateDTO(GovernmentDTO):
    rules: GovernmentRulesDTO
    initialized_on: date
    processed_on: date
    parties: list[PartyDTO] = Field(default_factory=list)
    policies: list[PolicyDTO] = Field(default_factory=list)
    results: list[ElectionResultDTO] = Field(default_factory=list)
    term: TermDTO | None = None
    pending_winner: int | None = None
    pending_year: int | None = None
    pending_president: int | None = None
    pending_vice: int | None = None
    cycle_year: int = 0
    finalists: list[int] = Field(default_factory=list)
    terms_won: dict[str, int] = Field(default_factory=dict)
    approval_history: list[dict[str, str | float]] = Field(default_factory=list)
    poll_history: list[dict[str, str | float]] = Field(default_factory=list)
    selic_decisions: list[SelicDecisionDTO] = Field(default_factory=list)
    treasury: Decimal
    reserved_spending: Decimal = Decimal(0)
    collected_tax: Decimal = Decimal(0)
    log: list[dict[str, str]] = Field(default_factory=list)
    revision: int = 0


class GovernmentActionDTO(GovernmentDTO):
    request_id: UUID | None = None
    action: Literal[
        "found",
        "join",
        "leave",
        "contribute",
        "nominate",
        "accept_candidate",
        "accept_vice",
        "decline_candidate",
        "decline_vice",
        "expel",
        "donate",
        "propose",
        "withdraw",
        "selic",
    ]
    party_id: int | None = None
    member_id: int | None = None
    vice_id: int | None = None
    name: str = Field(default="", max_length=70)
    acronym: str = Field(default="", max_length=5)
    color: str = Field(default="chart-1", pattern=r"^chart-(?:[1-9]|10)$")
    promise: float = Field(default=3, ge=1, le=5)
    amount: Decimal = Field(
        default=Decimal(0), ge=0, le=Decimal(1000000000), decimal_places=2
    )
    kind: PolicyKind = "COMMON_TAX"
    target: str = Field(default="", max_length=120)
    value: Decimal = Field(default=Decimal(0), ge=Decimal(-1), le=Decimal(1000000000))
    policy_id: int | None = None


class GovernmentImpactDTO(GovernmentDTO):
    ticker: str
    sector: str | None
    source: str
    covered: bool
    baseline_price: float
    effective_price: float
    impact: float
    product_effect: float
    monetary_effect: float
    exposures: list[ProductExposureDTO]


class PartyRankingDTO(GovernmentDTO):
    party_id: int
    name: str
    members: list[str]
    networth: Decimal


class CurrentTaxDTO(GovernmentDTO):
    label: str
    value: Decimal
    unit: Literal["money", "percent"] = "percent"


class GovernmentViewDTO(GovernmentDTO):
    state: GovernmentStateDTO
    today: date
    election_year: int
    phase: str
    can_govern: bool
    trading_frozen: bool
    users: dict[str, str]
    my_id: int
    impacts: list[GovernmentImpactDTO]
    party_ranking: list[PartyRankingDTO]
    president_portfolio: dict[str, int]
    president_finances: PortfolioDTO | None = None
    current_selic: float
    current_inflation: float
    inflation_delta: float
    selic_delta: float
    next_selic_meeting: date | None
    approval_factors: dict[str, float]
    current_taxes: list[CurrentTaxDTO]


class GovernmentPreviewDTO(GovernmentDTO):
    as_of: date
    horizon_days: int
    earliest_effective_on: date
    inflation_delta: float
    impacts: list[GovernmentImpactDTO]
    assumptions: str
