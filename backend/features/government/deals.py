"""
Os acordos de apoio por emenda: o governo paga a bancada de um partido, e o líder dela
orienta Sim em tudo o que o governo propuser. Aqui moram o preço da cadeira, a resposta do
partido do computador, os grupos que a emenda e a quebra atingem e o acordo em si; tudo é
função pura sobre números, e o estado da partida guarda os acordos.
"""

import calendar
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import DealBreaker, DealStatus, VoterGroup, VoterValue

ZERO = Decimal(0)

# Quanto uma cadeira custa por ano, em fração do PIB (0,005%); o centrão cobra uma vez e meia
SEAT_PRICE = Decimal("0.00005")
CENTRAO = "UPR"
CENTRAO_FACTOR = Decimal("1.5")

# O acordo vale 6 meses, e o partido de jogador tem 15 dias para responder
TERM_MONTHS = 6
ANSWER_DAYS = 15
# Depois de uma recusa, nova proposta ao mesmo partido só em 30 dias
RETRY_DAYS = 30
# Um mês antes do fim o governo propõe de novo
RENEW_DAYS = 31

# O partido do computador (fora o centrão) aceita com ao menos 2 das 3 bandeiras em comum com o governo
SHARED_FLAGS = 2

# Rejeição somada na quebra, cheia no grupo em que o outro lado é mais forte, e o apoio
# que o acordo soma por mês nesses grupos
BREAK_REJECTION = Decimal(8)
MONTHLY_SUPPORT = Decimal(1)


@dataclass
class Deal:
    """Um acordo de apoio, da proposta ao fim."""

    id: int
    # A bancada na casa em exercício; o partido na partida é nulo no do computador que não concorreu
    bloc_key: int
    party_id: int | None
    abbr: str
    seats: int
    # O preço mensal, em fração do PIB por ano
    ratio: Decimal
    proposed: date
    proposer_id: int
    status: DealStatus = DealStatus.PENDING
    # O prazo da resposta do partido de jogador; nulo no do computador, que responde no pregão seguinte
    answer_by: date | None = None
    answered: date | None = None
    start: date | None = None
    end: date | None = None
    broken_by: DealBreaker | None = None

    def covers(self, day: date) -> bool:
        """O acordo vigorou no dia, mesmo se acabou depois."""
        return (
            self.status in (DealStatus.ACTIVE, DealStatus.BROKEN, DealStatus.CUT)
            and self.start is not None
            and self.end is not None
            and self.start <= day <= self.end
        )

    def in_force(self, day: date) -> bool:
        return self.status is DealStatus.ACTIVE and self.covers(day)

    @property
    def is_computer(self) -> bool:
        return self.answer_by is None


def price(abbr: str, seats: int) -> Decimal:
    """Quanto a bancada custa por ano, em fração do PIB."""
    factor = CENTRAO_FACTOR if abbr == CENTRAO else Decimal(1)
    return SEAT_PRICE * seats * factor


def shared_flags(
    ally: Iterable[VoterValue] | None, government: Iterable[VoterValue] | None
) -> int:
    """Quantas bandeiras os dois partidos têm em comum."""
    return len(set(ally or ()) & set(government or ()))


def computer_accepts(
    abbr: str,
    ally_flags: Iterable[VoterValue] | None,
    government_flags: Iterable[VoterValue] | None,
) -> bool:
    """O centrão aceita sempre; os outros, só quando os valores do governo combinam com os deles."""
    if abbr == CENTRAO:
        return True
    return shared_flags(ally_flags, government_flags) >= SHARED_FLAGS


def group_weights(mix: Mapping[VoterGroup, Decimal]) -> dict[VoterGroup, Decimal]:
    """Quanto a emenda e a quebra atingem cada grupo: cheia (1) onde o partido é mais forte, proporcional nos outros."""
    top = max(mix.values(), default=ZERO)
    if top <= 0:
        return dict.fromkeys(VoterGroup, Decimal(1))
    return {g: mix.get(g, ZERO) / top for g in VoterGroup}


def strongest_groups(
    mix: Mapping[VoterGroup, Decimal], count: int = 2
) -> list[VoterGroup]:
    """Os grupos em que o partido é mais forte, do maior para o menor."""
    return sorted(VoterGroup, key=lambda g: (-mix.get(g, ZERO), g.value))[:count]


def break_rejection(mix: Mapping[VoterGroup, Decimal]) -> dict[VoterGroup, Decimal]:
    """A rejeição que a quebra soma em cada grupo."""
    return {g: BREAK_REJECTION * w for g, w in group_weights(mix).items()}


def month_support(mix: Mapping[VoterGroup, Decimal]) -> dict[VoterGroup, Decimal]:
    """O apoio que um mês de acordo soma ao partido aliado em cada grupo."""
    return {g: MONTHLY_SUPPORT * w for g, w in group_weights(mix).items()}


def add_months(day: date, months: int) -> date:
    index = day.month - 1 + months
    year, month = day.year + index // 12, index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def last_day(start: date, cap: date | None) -> date:
    """O último dia do acordo: 6 meses a partir do início, ou a véspera da posse do novo Congresso."""
    end = add_months(start, TERM_MONTHS) - timedelta(days=1)
    return min(end, cap) if cap is not None else end


def retry_from(declined: date) -> date:
    return declined + timedelta(days=RETRY_DAYS)


def amendments(deals: Iterable[Deal], reference: date) -> Decimal:
    """O que os acordos que vigoravam em `reference` pagam por ano, em fração do PIB."""
    return sum((d.ratio for d in deals if d.covers(reference)), ZERO)
