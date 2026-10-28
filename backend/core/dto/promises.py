"""As promessas de campanha da chapa: o que se promete, o que rende e como o mandato cumpre."""

from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO
from backend.core.enum import MeasureKind, PromiseState, VoterGroup, VoterValue

# Resposta


class PromiseDTO(BaseDTO):
    """Uma medida prometida, pública: o alvo, o "era" no anúncio e o dia do anúncio."""

    kind: MeasureKind
    # A medida escrita como o jogo escreve: "Ações: IR do day trade em 10%"
    title: str
    # Nulo na medida de setor, que é sim ou não
    target: Decimal | None
    baseline: Decimal | None
    sector: str | None
    segment: str | None
    announced: date


class PromiseRecordDTO(BaseDTO):
    """As promessas que um partido levou a uma eleição que passou."""

    election_year: int
    elected: bool
    promises: list[PromiseDTO]


class PromiseRowDTO(BaseDTO):
    """O que uma promessa faz num grupo de eleitores."""

    group: VoterGroup
    # O grupo quer o que a promessa faz (reação positiva)
    wanted: bool
    # Apoio que a promessa rende hoje no grupo, já descontado pela rejeição (negativo tira)
    support: Decimal
    # O mesmo apoio sem o desconto da rejeição
    support_full: Decimal
    # Rejeição do seu partido no grupo hoje
    rejection: Decimal
    # Cumprida: afinidade que soma e rejeição que repara
    loyalty: Decimal
    repair: Decimal
    # Descumprida: rejeição que soma
    breach: Decimal


class PromiseValueDTO(BaseDTO):
    """Quanto a promessa cumprida avança (positivo) ou recua (negativo) um valor."""

    value: VoterValue
    effect: Decimal


class PromisePreviewDTO(BaseDTO):
    promise: PromiseDTO
    # Os valores que a medida move, quando cumprida
    values: list[PromiseValueDTO]
    rows: list[PromiseRowDTO]


class PromiseTotalRowDTO(BaseDTO):
    """A soma das promessas num grupo: o apoio que rendem hoje, e o que a retirada custa."""

    group: VoterGroup
    support: Decimal
    # Rejeição que voltar atrás nas promessas já anunciadas soma neste grupo
    retreat: Decimal


class PromisesPreviewDTO(BaseDTO):
    """A lista de promessas como ficaria, uma linha por promessa e a soma por grupo."""

    items: list[PromisePreviewDTO]
    totals: list[PromiseTotalRowDTO]


class PromiseEffectDTO(BaseDTO):
    """O que o balanço deixa num grupo: afinidade somada e rejeição somada (negativa repara)."""

    group: VoterGroup
    loyalty: Decimal
    rejection: Decimal


class PromiseProgressDTO(BaseDTO):
    """Uma promessa do mandato em curso e o caminho já andado."""

    promise: PromiseDTO
    state: PromiseState
    # Fração do caminho do "era" ao alvo: 1 cumprida, 0 nada, negativa na direção contrária
    done: Decimal
    # O que a medida vale hoje no país; nulo na medida de setor
    current: Decimal | None


class BalanceItemDTO(BaseDTO):
    promise: PromiseDTO
    state: PromiseState
    done: Decimal
    # O que a promessa deixou em cada grupo; só os filiados do partido veem
    effects: list[PromiseEffectDTO]


class BalanceDTO(BaseDTO):
    """O balanço das promessas de um governo, no fim do mandato ou no impeachment sem vice."""

    term_start: date
    date: date
    party_id: int
    party_abbr: str
    party_color: str | None
    impeached: bool
    items: list[BalanceItemDTO]
    # A soma por grupo; vazia para quem não é do partido
    totals: list[PromiseEffectDTO]


class TermPromisesDTO(BaseDTO):
    """As promessas da chapa que governa, no cartão do Governo."""

    party_id: int
    party_abbr: str
    items: list[PromiseProgressDTO]
    # Metade do balanço já pesa no voto desde que as chapas fecharam
    weighed: bool
    # O último voto do Congresso que ainda entra em vigor antes do fim do mandato
    last_vote: date | None
    # "Se o mandato acabasse hoje", por grupo; vazio para quem não é do partido
    projection: list[PromiseEffectDTO]


class PromiseOptionDTO(BaseDTO):
    """Uma medida geral que se pode prometer: o que vale hoje e o passo de referência."""

    kind: MeasureKind
    baseline: Decimal
    step: Decimal
    # Maior alvo possível; nulo no teto de isenção, que não tem limite
    limit: Decimal | None


# Pedido


class PromiseRequest(BaseDTO):
    kind: MeasureKind
    # Obrigatório nas medidas gerais; as de setor são sim ou não
    target: Decimal | None = None
    sector: str | None = None
    segment: str | None = None


class PromisesRequest(BaseDTO):
    promises: list[PromiseRequest]
