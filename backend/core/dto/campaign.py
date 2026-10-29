"""As ações de campanha do partido, como o cartão e o histórico as mostram."""

from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import (
    CampaignActionKind,
    CampaignEntryKind,
    DiceBand,
    VoterGroup,
)

# Resposta


class DiceBandDTO(BaseDTO):
    """Uma faixa do dado de uma ação: onde cai, com que chance e o que muda."""

    band: DiceBand
    first_roll: int
    last_roll: int
    # Chance de 0 a 1
    chance: Decimal
    # Mudança do apoio de quem a ação atinge (o rival, no ataque), em pontos
    support: Decimal
    # Mudança da rejeição do seu partido no grupo: negativa repara, positiva é a culatra
    rejection: Decimal


class CampaignTargetDTO(BaseDTO):
    """Uma ação aplicada a um grupo (ou a todos, na TV), com o dado que ela rolaria hoje."""

    # Nulo na TV, que atinge todos os grupos
    group: VoterGroup | None
    # Quantas vezes o partido já fez a ação nesse grupo no mês e quanto ela rende agora
    uses_this_month: int
    rate: Decimal
    # Quanto do limite de reparação da campanha ainda cabe no grupo e o limite inteiro
    repair_left: Decimal
    repair_limit: Decimal
    # O apoio e a rejeição de hoje do seu partido no grupo; nulos na TV. No 2º turno o
    # apoio é o voto do partido no grupo (em cada 100 do grupo)
    support: Decimal | None
    rejection: Decimal | None
    bands: list[DiceBandDTO]
    # O efeito médio no apoio de quem a ação atinge
    average: Decimal


class CampaignActionDTO(BaseDTO):
    action: CampaignActionKind
    price: Decimal
    # O que falta no caixa para pagar; zero quando cobre
    missing: Decimal
    # A TV rola dois dados e vale o maior
    advantage: bool
    targets: list[CampaignTargetDTO]


class CampaignRivalDTO(BaseDTO):
    party_id: int
    abbr: str
    name: str
    color: str | None


class CampaignEntryDTO(BaseDTO):
    """Uma linha do histórico: uma ação, a verba de base ou um ataque recebido."""

    id: int
    date: date
    kind: CampaignEntryKind
    # Quem fez, pelo apelido; nulo na verba de base e no partido do computador
    nickname: str | None
    # O partido que agiu (o atacante, nos ataques recebidos)
    party_abbr: str
    party_color: str | None
    group: VoterGroup | None
    # O alvo do ataque, pela sigla
    rival_abbr: str | None
    # Os dados rolados e o que valeu; vazios na verba e no ataque recebido (o dado é do rival)
    rolls: list[int]
    roll: int | None
    band: DiceBand | None
    # Efeito no dia: apoio de quem a ação atinge (por grupo) e rejeição do partido que agiu
    support: Decimal
    rejection: Decimal
    # Quanto vale hoje, já com a queda, e a fração do efeito que sobra (de 0 a 1)
    worth_now: Decimal
    worth_share: Decimal
    # O que foi pago; nulo no ataque recebido
    price: Decimal | None
    # Sai no jornal: viral, desastre e todo ataque
    newsworthy: bool


class CampaignGroupDTO(BaseDTO):
    group: VoterGroup
    # O que a campanha soma hoje ao apoio do partido no grupo, já com a queda
    campaign: Decimal
    # No 2º turno: os indecisos do grupo hoje, em cada 100 eleitores dele; nulo no 1º turno
    undecided: Decimal | None


class CampaignPanelDTO(BaseDTO):
    """O cartão de ações de campanha do partido de quem vê."""

    party_id: int
    party_abbr: str
    # O dia da partida em que o cartão foi montado
    today: date
    # Se as ações estão abertas hoje; fechadas, `closed_reason` explica
    open: bool
    closed_reason: str | None
    campaign_start: date
    first_round: date
    # Quanto do apoio de hoje ainda vale no 1º turno, de 0 a 1
    share_at_vote: Decimal
    actions: list[CampaignActionDTO]
    rivals: list[CampaignRivalDTO]
    groups: list[CampaignGroupDTO]
    recent: list[CampaignEntryDTO]
    # Gastos em ações e verba de base da campanha
    actions_spent: Decimal
    actions_count: int
    base_spent: Decimal
    base_charges: int
    # A última cobrança da verba de base e o apoio que ela rendeu em cada grupo
    last_charge_date: date | None
    last_charge_amount: Decimal | None
    last_charge_points: Decimal | None


class CampaignHistoryDTO(BaseDTO):
    entries: list[CampaignEntryDTO]


class CampaignRollDTO(BaseDTO):
    """O resultado de uma ação recém-rolada."""

    entry: CampaignEntryDTO
    # O apoio e a rejeição de quem a ação atinge no grupo, antes e depois; nulos na TV
    target_abbr: str | None
    support_before: Decimal | None
    support_after: Decimal | None
    rejection_before: Decimal | None
    rejection_after: Decimal | None


# Pedido


class CampaignActionRequest(BaseDTO):
    action: CampaignActionKind
    # Obrigatório fora da TV
    group: VoterGroup | None = None
    # Obrigatório no ataque
    rival_id: int | None = None
