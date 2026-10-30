"""
As promessas de campanha: o que a chapa promete, quanto a promessa rende em cada grupo
e o que o cumprimento deixa no fim do mandato. Tudo aqui é função pura sobre números;
o estado da partida guarda as promessas e o resultado dos balanços.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from backend.core.enum import MeasureKind, PromiseState, VoterGroup, VoterValue
from backend.core.utils import required
from backend.features.government import spending, voters

ZERO = Decimal(0)
ONE = Decimal(1)

# Até 3 promessas por chapa
MAX_PROMISES = 3
# Pontos de apoio que a promessa rende por passo de referência e por unidade de reação do grupo
GAIN = Decimal(4)
# Cumprida: afinidade somada e rejeição reparada, por passo e unidade de reação, nos grupos que queriam
LOYALTY = Decimal(3)
REPAIR = Decimal(8)
# Descumprida: rejeição somada nos grupos que queriam; na direção contrária, 1,5 vez a cheia
BREAK = Decimal(8)
CONTRARY_FACTOR = Decimal("1.5")
# Voltar atrás depois do anúncio custa metade da rejeição de descumprir
RETREAT_SHARE = Decimal("0.5")
# Com as chapas fechadas, metade do efeito do que está em vigor já pesa no voto
WEIGHED_SHARE = Decimal("0.5")
# Quantas promessas o partido do computador faz
COMPUTER_PROMISES = 2
# As medidas gerais que se prometem: as que têm um valor em vigor
GENERAL_KINDS = tuple(kind for kind in MeasureKind if not kind.is_sector)
# Entre elas, os impostos; o resto é gasto público
TAX_KINDS = tuple(kind for kind in GENERAL_KINDS if not kind.is_spending)


@dataclass(frozen=True)
class Promise:
    """Uma medida prometida: o alvo, o que valia no anúncio e quando foi anunciada."""

    kind: MeasureKind
    # O valor prometido; nulo na medida de setor, que é sim ou não
    target: Decimal | None
    # O que valia no dia do anúncio ("era"); nulo na medida de setor
    baseline: Decimal | None
    sector: str | None
    segment: str | None
    announced: date

    @property
    def key(self) -> tuple[MeasureKind, str | None, str | None]:
        """A mesma medida no mesmo alvo é a mesma promessa."""
        return (self.kind, self.sector, self.segment)


@dataclass(frozen=True)
class GroupEffect:
    """O que o balanço de uma promessa deixa num grupo; a rejeição vem com sinal."""

    loyalty: Decimal
    rejection: Decimal


GroupEffects = dict[VoterGroup, GroupEffect]


def limit_of(kind: MeasureKind) -> Decimal | None:
    """O maior valor que uma medida geral leva: 100% nas alíquotas, o teto do gasto nos gastos e nenhum na isenção das vendas."""
    if kind is MeasureKind.STOCK_EXEMPTION:
        return None
    return spending.LIMITS.get(kind, ONE)


def promisable(kind: MeasureKind) -> bool:
    """O imposto geral e a isenção de setor se prometem; somar pontos ao IR de um setor, não."""
    return kind is not MeasureKind.SECTOR_TAX


def effects(promise: Promise) -> dict[VoterValue, Decimal]:
    """O quanto a promessa cumprida avança (positivo) ou recua cada valor."""
    return voters.measure_effects(promise.kind, promise.target, promise.baseline)


def reaction(group: VoterGroup, promise: Promise) -> Decimal:
    """Quanto o grupo quer o que a promessa faz: positivo quer, negativo não quer."""
    return voters.measure_reaction(
        group, promise.kind, promise.target, promise.baseline
    )


def wanted(group: VoterGroup, promise: Promise) -> Decimal:
    """A parte da reação em que o grupo quer a promessa; onde não quer, zero."""
    return max(ZERO, reaction(group, promise))


def yield_of(promise: Promise, group: VoterGroup, rejection: Decimal) -> Decimal:
    """
    O apoio que a promessa rende no grupo. Quem quer a medida rende multiplicado por
    (1 - rejeição ÷ 100): com 40 de rejeição, a promessa rende 60%. Quem não quer tira o
    apoio cheio.
    """
    gain = GAIN * reaction(group, promise)
    if gain > 0:
        return gain * (ONE - rejection / voters.HUNDRED)
    return gain


def campaign_yield(
    promises: Iterable[Promise], group: VoterGroup, rejection: Decimal
) -> Decimal:
    return sum((yield_of(p, group, rejection) for p in promises), ZERO)


def progress(promise: Promise, current: Decimal | None, exempt: bool) -> Decimal:
    """
    Quanto do caminho entre o "era" e o alvo o país já andou: 1 é cumprida, 0,5 é metade,
    negativo é a direção contrária (de 20% para 25% numa promessa de 10% anda -50%).
    A medida de setor é sim ou não.
    """
    if promise.kind.is_sector:
        return ONE if exempt else ZERO
    target = required(promise.target)
    baseline = required(promise.baseline)
    distance = target - baseline
    if distance == 0:
        return ZERO
    walked = (baseline if current is None else current) - baseline
    return max(-ONE, min(ONE, walked / distance))


def state_of(done: Decimal) -> PromiseState:
    if done >= 1:
        return PromiseState.FULFILLED
    if done > 0:
        return PromiseState.IN_PROGRESS
    if done < 0:
        return PromiseState.CONTRARY
    return PromiseState.UNTOUCHED


def settle(promise: Promise, done: Decimal) -> GroupEffects:
    """
    O balanço de uma promessa em cada grupo que a queria: cumprida soma afinidade e repara
    a rejeição na proporção do caminho; o que faltou soma rejeição, e a direção contrária
    soma 1,5 vez a de não ter feito nada. Quem não queria a medida não é cobrado.
    """
    result: GroupEffects = {}
    for group in VoterGroup:
        want = wanted(group, promise)
        gained = max(ZERO, done)
        missing = ONE - done if done >= 0 else CONTRARY_FACTOR
        result[group] = GroupEffect(
            loyalty=LOYALTY * gained * want,
            rejection=BREAK * missing * want - REPAIR * gained * want,
        )
    return result


def total(parts: Iterable[GroupEffects]) -> GroupEffects:
    """A soma dos balanços de várias promessas em cada grupo."""
    result = {g: GroupEffect(ZERO, ZERO) for g in VoterGroup}
    for part in parts:
        for group, effect in part.items():
            now = result[group]
            result[group] = GroupEffect(
                now.loyalty + effect.loyalty, now.rejection + effect.rejection
            )
    return result


def scaled(effects_: GroupEffects, factor: Decimal) -> GroupEffects:
    return {
        g: GroupEffect(e.loyalty * factor, e.rejection * factor)
        for g, e in effects_.items()
    }


def remaining(full: GroupEffects, applied: GroupEffects) -> GroupEffects:
    """O que falta fechar do balanço depois do que já pesou no voto."""
    zero = GroupEffect(ZERO, ZERO)
    return {
        g: GroupEffect(
            e.loyalty - applied.get(g, zero).loyalty,
            e.rejection - applied.get(g, zero).rejection,
        )
        for g, e in full.items()
    }


def retreat(old: Promise, new: Promise | None) -> dict[VoterGroup, Decimal]:
    """
    A rejeição que sai de voltar atrás depois do anúncio, nos grupos que queriam o que
    deixou de ser prometido: retirar ou trocar custa metade do descumprimento da promessa
    inteira; baixar o alvo custa metade do pedaço abandonado; subir o alvo não custa.
    """
    dropped = _dropped(old, new)
    if dropped is None:
        return dict.fromkeys(VoterGroup, ZERO)
    value, before = dropped
    return {
        g: RETREAT_SHARE
        * BREAK
        * max(ZERO, voters.measure_reaction(g, old.kind, value, before))
        for g in VoterGroup
    }


def backs_down(old: Promise, new: Promise | None) -> bool:
    """Se a lista nova abandona parte da promessa já anunciada: retirar, trocar ou baixar o alvo."""
    return _dropped(old, new) is not None


def _dropped(
    old: Promise, new: Promise | None
) -> tuple[Decimal | None, Decimal | None] | None:
    """O pedaço da promessa que deixou de valer, como valor e "era" da medida; nulo quando nada foi abandonado."""
    if new is None or old.kind.is_sector:
        return old.target, old.baseline
    old_walk = required(old.target) - required(old.baseline)
    new_walk = required(new.target) - required(old.baseline)
    same_side = old_walk * new_walk > 0
    if not same_side:
        return old.target, old.baseline
    if abs(new_walk) < abs(old_walk):
        return old.target, new.target
    return None


def to_payload(promise: Promise) -> dict[str, object]:
    return {
        "kind": promise.kind.value,
        "target": None if promise.target is None else str(promise.target),
        "baseline": None if promise.baseline is None else str(promise.baseline),
        "sector": promise.sector,
        "segment": promise.segment,
        "announced": promise.announced.isoformat(),
    }


def effects_to_payload(effects_: GroupEffects) -> dict[str, dict[str, str]]:
    return {
        g.value: {"loyalty": str(e.loyalty), "rejection": str(e.rejection)}
        for g, e in effects_.items()
    }


def effects_from_payload(payload: Mapping[str, Mapping[str, Any]]) -> GroupEffects:
    return {
        VoterGroup(key): GroupEffect(
            Decimal(str(values["loyalty"])), Decimal(str(values["rejection"]))
        )
        for key, values in payload.items()
    }


def from_payload(payload: Mapping[str, Any]) -> Promise:
    target = payload.get("target")
    baseline = payload.get("baseline")
    sector = payload.get("sector")
    segment = payload.get("segment")
    return Promise(
        kind=MeasureKind(str(payload["kind"])),
        target=None if target is None else Decimal(str(target)),
        baseline=None if baseline is None else Decimal(str(baseline)),
        sector=None if sector is None else str(sector),
        segment=None if segment is None else str(segment),
        announced=date.fromisoformat(str(payload["announced"])),
    )


def computer_picks(
    radar: Mapping[VoterValue, Decimal],
    baselines: Mapping[MeasureKind, Decimal],
    day: date,
) -> list[Promise]:
    """
    O partido do computador promete por regra: das medidas gerais, as que mais avançam os
    valores do perfil dele, num passo de referência no sentido que o perfil quer.
    """
    scored: list[tuple[Decimal, Promise]] = []
    for kind, baseline in baselines.items():
        reference = voters.EFFECT_STEPS[kind]
        best: tuple[Decimal, Promise] | None = None
        for target in (baseline - reference, baseline + reference):
            limit = limit_of(kind)
            if target < 0 or (limit is not None and target > limit):
                continue
            promise = Promise(kind, target, baseline, None, None, day)
            score = sum(
                (
                    voters.affinity_weight(radar[v]) * effect
                    for v, effect in effects(promise).items()
                ),
                ZERO,
            )
            if score > 0 and (best is None or score > best[0]):
                best = (score, promise)
        if best is not None:
            scored.append(best)
    scored.sort(key=lambda item: (-item[0], item[1].kind.value))
    return [promise for _, promise in scored[:COMPUTER_PROMISES]]
