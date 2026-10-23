"""Eleições e governo determinísticos, guiados pela data simulada."""

import calendar
import hashlib
import math
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal

from backend.core.dto.government import (
    ElectionResultDTO,
    GovernmentActionDTO,
    GovernmentStateDTO,
    PartyDTO,
    PolicyDTO,
    SelicDecisionDTO,
    TermDTO,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.government.economy import (
    POLICIES,
    PRODUCTS,
    active_policies,
    campaign_gain,
)

ZERO = Decimal(0)
CENT = Decimal("0.01")


def draw(seed: int, key: str) -> float:
    return int.from_bytes(hashlib.sha256(f"{seed}:{key}".encode()).digest()[:8]) / 2**64


def note(state: GovernmentStateDTO, text: str) -> None:
    state.log = [
        *state.log[-299:],
        {"on": state.processed_on.isoformat(), "text": text},
    ]


def election_year(state: GovernmentStateDTO, on: date) -> int:
    first = state.initialized_on.year + 1
    return first + max(0, (on.year - first + 3) // 4) * 4


def phase(state: GovernmentStateDTO, on: date) -> str:
    year = election_year(state, on)
    if date(year - 1, 10, 7) <= on < date(year, 10, 7):
        return "campaign"
    if date(year, 10, 7) <= on <= date(year, 10, 28) and state.finalists:
        return "runoff"
    return "government"


def party_of(state: GovernmentStateDTO, actor: int) -> PartyDTO | None:
    return next((p for p in state.parties if actor in p.members), None)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConflictError(message)


def eligible(state: GovernmentStateDTO, p: PartyDTO) -> bool:
    return (
        p.campaign_active
        and p.candidate is not None
        and p.candidate_accepted
        and state.terms_won.get(str(p.candidate), 0) < 2
    )


def ensure_ai(state: GovernmentStateDTO) -> None:
    humans = [p for p in state.parties if not p.is_ai and eligible(state, p)]
    # Mantém identidade e programa do governante e o histórico dos adversários.
    # Somente as vagas necessárias participam da eleição corrente.
    count = max(0, 3 - len(humans))
    for p in state.parties:
        if p.is_ai:
            if (
                p.candidate is not None
                and state.terms_won.get(str(p.candidate), 0) >= 2
            ):
                p.candidate = min([0, *(x.candidate or 0 for x in state.parties)]) - 1
                p.candidate_name = f"Nova liderança do {p.acronym}"
            p.campaign_active = -p.id <= count
    for i in range(3):
        if any(p.id == -i - 1 for p in state.parties):
            continue
        existing = [p.promise for p in state.parties if eligible(state, p)]
        position = max(
            range(1, 6), key=lambda n: min((abs(n - x) for x in existing), default=3)
        )
        state.parties.append(
            PartyDTO(
                id=-i - 1,
                name=["União do Progresso", "Frente Cidadã", "Aliança do Equilíbrio"][
                    i
                ],
                acronym=["UPR", "FRC", "ALE"][i],
                color="neutral",
                founder=None,
                candidate=-i - 1,
                candidate_name=["Helena Prado", "Caio Alves", "Iara Lima"][i],
                candidate_accepted=True,
                promise=position,
                is_ai=True,
                campaign_active=i < count,
            )
        )


def polls(
    state: GovernmentStateDTO, year: int, seed: int, finalists: list[int] | None = None
) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    parties = [
        p
        for p in state.parties
        if eligible(state, p) and (not finalists or p.id in finalists)
    ]
    total = dict.fromkeys((str(p.id) for p in parties), 0.0)
    by_profile: dict[str, dict[str, float]] = {}
    weights = sum(g.weight for g in state.rules.electorate)
    for group in state.rules.electorate:
        scores = {}
        for p in parties:
            value = -0.6 * (p.promise - group.position) ** 2
            value += group.campaign_sensitivity * math.log1p(p.support) * 0.7
            if state.term and state.term.president == p.candidate:
                value += (state.term.approval - 50) / 50
            value += (
                draw(
                    seed,
                    f"poll:{year}:{state.processed_on.year}-{state.processed_on.month}:{group.name}:{p.id}",
                )
                - 0.5
            ) * 0.12
            scores[str(p.id)] = math.exp(value)
        denominator = sum(scores.values()) or 1
        shares = {key: value / denominator * 100 for key, value in scores.items()}
        by_profile[group.name] = shares
        for key, value in shares.items():
            total[key] += value * group.weight / weights
    return total, by_profile


def approval_factors(
    state: GovernmentStateDTO, inflation: float, market_return: float
) -> dict[str, float]:
    if not state.term:
        return {}
    term = state.term
    party = next((p for p in state.parties if p.id == term.party_id), None)
    approved = [
        p
        for p in state.policies
        if p.party_id == term.party_id and p.status == "approved"
    ]
    position = (
        sum(p.position for p in approved) / len(approved)
        if approved
        else (party.promise if party else 3)
    )
    tax_effect = 0.0
    for p in active_policies(state, state.processed_on):
        if p.kind in ("PRODUCT_TARIFF", "PUBLIC_SPENDING") or p.effective_on is None:
            continue
        age = (state.processed_on - p.effective_on).days
        if age < 180:
            tax_effect += (
                -min(5, p.position) if p.position >= 4 else min(3, 4 - p.position)
            ) * (1 - age / 180)
    return {
        "Inflação": 4
        if inflation <= state.rules.inflation_target
        else -3 * (inflation - state.rules.inflation_target) * 100,
        "Bolsa em 12 meses": max(-6, min(6, market_return / 0.05)),
        "Medidas tributárias": tax_effect,
        "Promessa": -3 * abs(position - (party.promise if party else 3)),
    }


def propose(
    state: GovernmentStateDTO, actor: int, command: GovernmentActionDTO
) -> None:
    term = state.term
    require(
        term is not None and not term.neutral and term.president == actor,
        "Só o presidente em exercício pode propor medidas.",
    )
    assert term is not None
    kind, value, target = command.kind, command.value, command.target.strip()
    if kind in ("COMMON_TAX", "DAY_TRADE_TAX", "FII_TAX", "LCI_TAX"):
        require(0 <= value <= Decimal("0.50"), "A alíquota deve ficar entre 0% e 50%.")
        target = ""
    elif kind == "STOCK_EXEMPTION":
        require(
            0 <= value <= 1000000,
            "O limite de isenção deve ficar entre zero e um milhão.",
        )
        target = ""
    elif kind == "FIXED_TAX_SHIFT":
        require(
            Decimal("-0.225") <= value <= Decimal("0.275"),
            "O ajuste da renda fixa deve ficar entre -22,5 e +27,5 pontos percentuais.",
        )
        target = ""
    elif kind == "SECTOR_TAX":
        require(
            target
            in {s for c in state.rules.companies for s in (c.sector, c.segment) if s},
            "Escolha um setor ou segmento coberto pelo cenário.",
        )
        require(
            Decimal("-0.5") <= value <= Decimal("0.5"),
            "O ajuste setorial deve ficar entre -50 e +50 pontos.",
        )
    elif kind == "PRODUCT_TARIFF":
        require(
            target in PRODUCTS and 0 <= value <= 1,
            "Escolha um produto e uma tarifa entre 0% e 100%.",
        )
    elif kind == "PUBLIC_SPENDING":
        require(
            1000000 <= value <= 100000000,
            "Cada programa deve investir entre R$ 1 milhão e R$ 100 milhões.",
        )
        require(
            value <= state.treasury - state.reserved_spending,
            "O orçamento público livre não cobre esse programa.",
        )
    require(
        len([p for p in state.policies if p.status == "queued"]) < 20,
        "A fila do Congresso já tem 20 medidas.",
    )
    require(
        not any(
            p.status == "queued" and (p.kind, p.target) == (kind, target)
            for p in state.policies
        ),
        "Essa medida já está na fila. Retire a anterior antes de alterar.",
    )
    position = (
        4.5
        if kind == "PUBLIC_SPENDING"
        else 2
        if kind == "SECTOR_TAX" and value <= 0
        else 4
        if kind in ("SECTOR_TAX", "PRODUCT_TARIFF")
        else 1
        if (kind == "STOCK_EXEMPTION" and value >= 20000)
        or (kind != "STOCK_EXEMPTION" and value < Decimal("0.15"))
        else 5
    )
    state.policies.append(
        PolicyDTO(
            id=max((p.id for p in state.policies), default=0) + 1,
            kind=kind,
            target=target,
            value=value,
            proposed_on=state.processed_on,
            author=actor,
            party_id=term.party_id,
            position=position,
        )
    )
    note(
        state,
        f"Proposta pública: {POLICIES[kind]} {PRODUCTS.get(target, target)}. Votação no fechamento do mês; vigência após 90 dias da aprovação.",
    )


def action(
    state: GovernmentStateDTO,
    actor: int,
    command: GovernmentActionDTO,
    cash: Decimal,
    participants: set[int],
    baseline_selic: float,
    inflation: float,
) -> dict[int, Decimal]:
    debits: dict[int, Decimal] = {}
    own = party_of(state, actor)
    party = next(
        (p for p in state.parties if p.id == command.party_id and not p.is_ai), None
    )
    today = state.processed_on
    match command.action:
        case "found":
            require(own is None, "Saia do seu partido antes de fundar outro.")
            name, acronym = command.name.strip(), command.acronym.strip().upper()
            require(
                len(name) >= 3
                and 2 <= len(acronym) <= 5
                and acronym.isalpha()
                and acronym.isascii(),
                "Informe nome e sigla de 2 a 5 letras.",
            )
            require(
                not any(
                    p.acronym == acronym
                    or p.name.casefold() == name.casefold()
                    or p.color == command.color
                    for p in state.parties
                ),
                "Nome, sigla ou cor já usados por outro partido.",
            )
            state.parties.append(
                PartyDTO(
                    id=max([0, *(p.id for p in state.parties)]) + 1,
                    name=name,
                    acronym=acronym,
                    color=command.color,
                    founder=actor,
                    members=[actor],
                    contributions={str(actor): command.amount},
                    promise=command.promise,
                )
            )
            note(state, f"Fundado {acronym}; filiação e candidatura são opcionais.")
        case "join":
            require(
                own is None and party is not None,
                "Escolha um partido humano e tenha só uma filiação por vez.",
            )
            assert party is not None
            party.members.append(actor)
            party.contributions[str(actor)] = command.amount
            note(state, f"Jogador {actor} filiou-se ao {party.acronym}.")
        case "leave" | "expel":
            selected = own if command.action == "leave" else party
            target = actor if command.action == "leave" else command.member_id
            require(
                selected is not None and target in selected.members,
                "Filiação não encontrada.",
            )
            assert selected is not None and target is not None
            if command.action == "expel":
                require(
                    selected.founder == actor and target != actor,
                    "Só o fundador pode expulsar outro filiado.",
                )
            selected.members.remove(target)
            selected.contributions.pop(str(target), None)
            if selected.candidate == target:
                selected.candidate, selected.candidate_accepted = None, False
            if selected.vice == target:
                selected.vice, selected.vice_accepted = None, False
            if selected.founder == target:
                selected.founder = selected.members[0] if selected.members else None
            note(
                state,
                f"Jogador {target} {'saiu do' if command.action == 'leave' else 'foi expulso do'} {selected.acronym}. Contribuição encerrada.",
            )
        case "contribute":
            require(
                own is not None, "Você precisa estar filiado para definir contribuição."
            )
            assert own is not None
            own.contributions[str(actor)] = command.amount
            note(state, f"Contribuição mensal de {actor}: R$ {command.amount}.")
        case "nominate":
            require(
                phase(state, today) == "campaign",
                "Chapas só podem ser inscritas durante a campanha.",
            )
            require(
                own is not None and own.founder == actor, "Só o fundador monta a chapa."
            )
            assert own is not None
            require(
                command.member_id in own.members and command.member_id in participants,
                "O candidato precisa ser um filiado.",
            )
            require(
                command.vice_id is None
                or (
                    command.vice_id in own.members
                    and command.vice_id != command.member_id
                ),
                "O vice precisa ser outro filiado.",
            )
            require(
                state.terms_won.get(str(command.member_id), 0) < 2,
                "O candidato já cumpriu dois mandatos consecutivos.",
            )
            own.candidate, own.vice = command.member_id, command.vice_id
            own.candidate_accepted, own.vice_accepted = (
                command.member_id == actor,
                False,
            )
            note(
                state,
                f"Chapa indicada no {own.acronym}. Convites aguardam aceite pessoal.",
            )
        case "decline_candidate" | "decline_vice":
            require(own is not None, "O convite não está disponível.")
            assert own is not None
            if command.action == "decline_candidate":
                require(own.candidate == actor, "Você não foi indicado para candidato.")
                own.candidate, own.candidate_accepted = None, False
            else:
                require(own.vice == actor, "Você não foi indicado para vice.")
                own.vice, own.vice_accepted = None, False
            note(
                state,
                f"Jogador {actor} recusou o convite do {own.acronym}, mantendo a filiação.",
            )
        case "accept_candidate" | "accept_vice":
            require(
                phase(state, today) == "campaign" and own is not None,
                "Convites só podem ser aceitos durante a campanha.",
            )
            assert own is not None
            if command.action == "accept_candidate":
                require(own.candidate == actor, "Você não foi indicado para candidato.")
                own.candidate_accepted = True
            else:
                require(own.vice == actor, "Você não foi convidado para vice.")
                own.vice_accepted = True
            note(state, f"Jogador {actor} aceitou a indicação do {own.acronym}.")
        case "donate":
            recipient = next(
                (p for p in state.parties if p.id == command.party_id), None
            )
            require(
                phase(state, today) == "runoff"
                and recipient is not None
                and recipient.id in state.finalists,
                "Doações avulsas só são permitidas aos finalistas entre os turnos.",
            )
            require(
                own is None or own.id not in state.finalists,
                "Filiados dos finalistas usam a contribuição mensal.",
            )
            require(
                0 < command.amount <= cash,
                "A doação deve ser positiva e caber no caixa disponível.",
            )
            assert recipient is not None
            recipient.spent += command.amount
            recipient.support += campaign_gain(
                command.amount, state.rules.campaign_scale
            )
            debits[actor] = command.amount
            note(
                state,
                f"Doação pública: jogador {actor} doou R$ {command.amount} ao {recipient.acronym}.",
            )
        case "propose":
            propose(state, actor, command)
        case "withdraw":
            require(
                state.term is not None and state.term.president == actor,
                "Só o presidente pode retirar medidas.",
            )
            policy = next(
                (
                    p
                    for p in state.policies
                    if p.id == command.policy_id and p.status == "queued"
                ),
                None,
            )
            require(policy is not None, "A medida já foi votada ou retirada.")
            assert policy is not None
            policy.status = "withdrawn"
            note(state, f"Medida {policy.id} retirada antes do voto.")
        case "selic":
            require(
                state.rules.manual_selic
                and state.term is not None
                and state.term.president == actor
                and not state.term.neutral,
                "A SELIC só pode ser decidida pelo presidente quando essa opção estiver ligada.",
            )
            last = state.selic_decisions[-1] if state.selic_decisions else None
            require(
                last is None or today >= last.on + timedelta(days=45),
                "A próxima reunião monetária ainda não chegou (intervalo de 45 dias).",
            )
            ceiling = (
                0.03
                if inflation > state.rules.inflation_target + 0.10
                else 0.015
                if inflation > state.rules.inflation_target + 0.02
                else 0.0075
            )
            previous = last.rate if last else baseline_selic
            require(
                0 <= command.value <= Decimal("1")
                and abs(float(command.value) - previous) <= ceiling + 1e-9,
                f"Nesta reunião a SELIC pode variar até {ceiling * 100:g} ponto(s) percentual(is).",
            )
            state.selic_decisions.append(
                SelicDecisionDTO(
                    on=today, rate=float(command.value), baseline=baseline_selic
                )
            )
            note(
                state,
                f"Decisão monetária pública: SELIC {float(command.value) * 100:.2f}% a.a.",
            )
    if (
        command.action
        in ("nominate", "accept_candidate", "decline_candidate", "leave", "expel")
        and phase(state, today) == "campaign"
    ):
        ensure_ai(state)
    return debits


def advance_day(
    state: GovernmentStateDTO,
    today: date,
    seed: int,
    balances: dict[int, Decimal],
    inflation: float,
    market_return: float,
    baseline_selic: float = 0.15,
) -> dict[int, Decimal]:
    state.processed_on = today
    debits: dict[int, Decimal] = {}
    year = election_year(state, today)
    if phase(state, today) == "campaign" and state.cycle_year != year:
        state.cycle_year = year
        state.finalists = []
        for p in state.parties:
            p.spent, p.support = ZERO, 0
        ensure_ai(state)
        votes, _ = polls(state, year, seed)
        state.poll_history.append({"on": today.isoformat(), **votes})
        note(state, f"Aberta a campanha da eleição de {year}.")
    if today.day == 1 and phase(state, today) in ("campaign", "runoff"):
        if phase(state, today) == "campaign":
            # Recalcula vagas, preservando o apoio dos adversários já conhecidos.
            ensure_ai(state)
        humans = [p for p in state.parties if not p.is_ai and eligible(state, p)]
        average = (
            sum((sum(p.contributions.values(), ZERO) for p in humans), ZERO)
            / max(1, len(humans))
            if humans
            else state.rules.campaign_scale
        )
        for p in state.parties:
            paid = ZERO
            if (p.is_ai and not eligible(state, p)) or (not p.is_ai and not p.members):
                continue
            if p.is_ai:
                paid = (
                    average
                    * {
                        "easy": Decimal("0.5"),
                        "medium": Decimal(1),
                        "hard": Decimal("1.5"),
                    }[state.rules.difficulty]
                )
            else:
                for member in p.members:
                    amount = min(
                        p.contributions.get(str(member), ZERO),
                        max(ZERO, balances.get(member, ZERO)),
                    )
                    amount = amount.quantize(CENT, rounding=ROUND_DOWN)
                    debits[member] = debits.get(member, ZERO) + amount
                    paid += amount
                    if amount < p.contributions.get(str(member), ZERO):
                        note(
                            state,
                            f"Contribuição de {member} limitada ao caixa disponível.",
                        )
            p.spent += paid
            p.support += campaign_gain(paid, state.rules.campaign_scale)
        votes, _ = polls(state, year, seed)
        state.poll_history.append({"on": today.isoformat(), **votes})
        note(
            state,
            "Pesquisa mensal publicada; contribuições de campanha contabilizadas.",
        )
    if today == date(year, 10, 7):
        ensure_ai_preserving(state)
        resolve_election(state, year, 1, seed)
    elif today == date(year, 10, 28) and state.finalists:
        resolve_election(state, year, 2, seed)
    if state.pending_year is not None and today >= date(state.pending_year + 1, 1, 1):
        president = state.pending_president
        assert president is not None and state.pending_winner is not None
        if not state.term or state.term.president != president:
            state.terms_won = {}
        state.terms_won[str(president)] = state.terms_won.get(str(president), 0) + 1
        state.term = TermDTO(
            party_id=state.pending_winner,
            president=president,
            vice=state.pending_vice,
            start=today,
            end=date(today.year + 4, 1, 1),
            neutral=president == -999,
        )
        (
            state.pending_year,
            state.pending_winner,
            state.pending_president,
            state.pending_vice,
        ) = None, None, None, None
        state.finalists = []
        note(
            state,
            f"Posse do presidente {president}. Carteira congelada enquanto exercer o cargo.",
        )
    if (
        state.rules.manual_selic
        and state.term
        and state.term.president < 0
        and not state.term.neutral
        and (
            not state.selic_decisions
            or today >= state.selic_decisions[-1].on + timedelta(days=45)
        )
    ):
        party = next((p for p in state.parties if p.id == state.term.party_id), None)
        previous_rate = (
            state.selic_decisions[-1].rate if state.selic_decisions else baseline_selic
        )
        # O mesmo intervalo e limite do jogador se aplicam ao presidente autônomo.
        direction = (
            1
            if inflation > state.rules.inflation_target
            else -1
            if party and party.promise >= 4
            else 0
        )
        rate = max(0, min(1, previous_rate + direction * 0.0075))
        action(
            state,
            state.term.president,
            GovernmentActionDTO(action="selic", value=Decimal(str(rate))),
            ZERO,
            set(),
            baseline_selic,
            inflation,
        )
    if today.day == calendar.monthrange(today.year, today.month)[1] and state.term:
        term = state.term
        term.approval = max(
            0,
            min(
                100,
                50 + sum(approval_factors(state, inflation, market_return).values()),
            ),
        )
        term.low_months = (
            term.low_months + 1
            if not term.neutral and term.approval < state.rules.impeachment_floor
            else 0
        )
        state.approval_history.append(
            {"on": today.isoformat(), "approval": term.approval}
        )
        if term.low_months >= state.rules.impeachment_months:
            previous = term.president
            term.president = term.vice if term.vice is not None else -999
            term.neutral = term.vice is None
            term.vice, term.low_months, term.approval = None, 0, 50
            for p in state.policies:
                if p.status == "queued":
                    p.status = "withdrawn"
            note(
                state,
                f"Impeachment de {previous}. Assume {term.president}; medidas aprovadas mantêm a vigência.",
            )
        if (
            term.president < 0
            and not term.neutral
            and not any(p.status == "queued" for p in state.policies)
        ):
            party = next((p for p in state.parties if p.id == term.party_id), None)
            if party:
                kind = "COMMON_TAX" if party.promise <= 3 else "PUBLIC_SPENDING"
                value = (
                    Decimal("0.12")
                    if kind == "COMMON_TAX"
                    else min(
                        Decimal(10000000),
                        max(ZERO, state.treasury - state.reserved_spending),
                    )
                )
                if kind != "PUBLIC_SPENDING" or value >= 1000000:
                    propose(
                        state,
                        term.president,
                        GovernmentActionDTO(action="propose", kind=kind, value=value),
                    )
        for p in state.policies:
            if p.status != "queued":
                continue
            passed = draw(seed, f"congress:{today}:{p.id}") < term.approval / 100
            if (
                p.kind == "PUBLIC_SPENDING"
                and p.value > state.treasury - state.reserved_spending
            ):
                passed = False
            p.status, p.voted_on = ("approved" if passed else "rejected"), today
            if passed:
                p.effective_on = today + timedelta(days=90)
                if p.kind == "PUBLIC_SPENDING":
                    state.reserved_spending += p.value
            note(
                state,
                f"Congresso: medida {p.id} {'aprovada; vigência em ' + str(p.effective_on) if passed else 'rejeitada'}.",
            )
    for p in state.policies:
        if p.status == "approved" and p.effective_on == today:
            if p.kind == "PUBLIC_SPENDING":
                state.treasury -= p.value
                state.reserved_spending -= p.value
            note(state, f"Medida {p.id} passou a valer.")
    return debits


def ensure_ai_preserving(state: GovernmentStateDTO) -> None:
    ensure_ai(state)


def resolve_election(
    state: GovernmentStateDTO, year: int, round_: int, seed: int
) -> None:
    votes, profiles = polls(state, year, seed, state.finalists if round_ == 2 else None)
    ordered = sorted(
        (int(key) for key in votes),
        key=lambda key: (-votes[str(key)], draw(seed, f"tie:{year}:{key}")),
    )
    winner = (
        ordered[0] if ordered and (round_ == 2 or votes[str(ordered[0])] > 50) else None
    )
    finalists = ordered[:2]
    state.results.append(
        ElectionResultDTO(
            year=year,
            round=round_,
            on=state.processed_on,
            votes=votes,
            by_profile=profiles,
            finalists=finalists,
            winner=winner,
        )
    )
    if not ordered:
        state.pending_winner, state.pending_year = 0, year
        state.pending_president, state.pending_vice = -999, None
        state.finalists = []
        note(
            state,
            "Sem candidaturas válidas no segundo turno. Governo neutro assume até a próxima eleição.",
        )
    elif winner is not None:
        party = next(p for p in state.parties if p.id == winner)
        state.pending_winner, state.pending_year = winner, year
        state.pending_president, state.pending_vice = (
            party.candidate,
            party.vice if party.vice_accepted else None,
        )
        state.finalists = []
        note(
            state,
            f"Eleição encerrada: {party.acronym} eleito com {votes[str(winner)]:.2f}% dos votos válidos. Posse em 1º de janeiro.",
        )
    else:
        state.finalists = finalists
        note(
            state,
            "Ninguém superou 50% dos votos válidos. Segundo turno em 28 de outubro.",
        )
