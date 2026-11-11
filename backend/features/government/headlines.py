"""
As manchetes da política no jornal da partida. Cada uma conta o fato para a sala inteira,
na terceira pessoa; os números de campanha (dado, pontos de apoio) ficam com o partido.
"""

from datetime import date
from decimal import Decimal

from backend.core.enum import (
    CampaignActionKind,
    DiceBand,
    MeasureKind,
    NewsType,
    VoterGroup,
)
from backend.core.utils import format_money
from backend.features.government.measures import MONTHS, number, percent
from backend.features.newsroom.text import number as precise_number
from backend.features.newsroom.text import pick
from backend.features.notifications.news import Headline

# Quem chama compõe a semente (partida, dia e fato); a sala inteira lê o mesmo texto e a
# releitura do mesmo fato dá o mesmo resultado
Seed = tuple[object, ...]
Wordings = tuple[str, str, str]

GROUP_NAMES: dict[VoterGroup, str] = {
    VoterGroup.INVESTORS: "investidores",
    VoterGroup.ENTREPRENEURS: "empreendedores",
    VoterGroup.FORMAL_WORKERS: "trabalhadores com carteira",
    VoterGroup.PUBLIC_SERVANTS: "servidores",
    VoterGroup.RETIREES: "aposentados",
    VoterGroup.WELFARE: "quem depende de auxílio",
}

HUNDRED = Decimal(100)

# O que cada medida de gasto paga, como a manchete a chama
SPENDING_NOUNS: dict[MeasureKind, str] = {
    MeasureKind.WELFARE_SPENDING: "auxílio",
    MeasureKind.SERVANT_RAISE: "servidores",
    MeasureKind.RETIREE_RAISE: "aposentadorias",
    MeasureKind.PUBLIC_WORKS: "obras",
    MeasureKind.OPERATING_COST: "custeio",
}


def _day_month(day: date) -> str:
    return f"{day.day:02d}/{day.month:02d}"


def _month_year(day: date) -> str:
    return f"{MONTHS[day.month - 1]} {day.year}"


def _share(share: Decimal) -> str:
    return f"{number(share * HUNDRED)}%"


def _among(group: VoterGroup) -> str:
    """O complemento "entre os aposentados", que no auxílio vira "entre quem depende de auxílio"."""
    name = GROUP_NAMES[group]
    return f"entre {name}" if group is VoterGroup.WELFARE else f"entre os {name}"


def _with(group: VoterGroup) -> str:
    name = GROUP_NAMES[group]
    return f"com {name}" if group is VoterGroup.WELFARE else f"com os {name}"


def _abbrs(*values: str | None) -> tuple[str, ...]:
    """As siglas citadas na manchete, na ordem do texto; o que é nulo não entra."""
    return tuple(value for value in values if value)


def _wording(options: Wordings, seed: Seed, part: str = "title") -> str:
    """Uma das três redações do fato; título e linha fina sorteiam separados."""
    return pick(options, *seed, part)


def _join(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} e {items[-1]}"


# Calendário da eleição


def campaign_opened(
    first_round: date, ticket_deadline: date, *, seed: Seed
) -> Headline:
    deadline = _day_month(ticket_deadline)
    vote = _day_month(first_round)
    return Headline(
        NewsType.CAMPAIGN_OPENED,
        _wording(
            (
                f"Começa a campanha para a eleição de {_month_year(first_round)}",
                f"Abre a campanha eleitoral de {_month_year(first_round)}",
                f"Está aberta a campanha para a eleição de {_month_year(first_round)}",
            ),
            seed,
        ),
        _wording(
            (
                f"As chapas fecham em {deadline} e o 1º turno é em {vote}. Já dá para "
                "inscrever a chapa, fazer comício, evento e propaganda na TV.",
                f"O 1º turno é em {vote}, e as chapas fecham em {deadline}. A partir de "
                "hoje os partidos podem inscrever a chapa, fazer comício, evento e "
                "propaganda na TV.",
                f"Os partidos têm até {deadline} para inscrever as chapas, e as urnas "
                f"abrem em {vote}. Comício, evento e propaganda na TV já estão liberados.",
            ),
            seed,
            "dek",
        ),
    )


def tickets_closing(ticket_deadline: date, *, seed: Seed) -> Headline:
    deadline = _day_month(ticket_deadline)
    return Headline(
        NewsType.ELECTION_CALENDAR,
        _wording(
            (
                f"Chapas fecham em {deadline}",
                f"Prazo das chapas termina em {deadline}",
                f"Partidos têm até {deadline} para registrar as chapas",
            ),
            seed,
        ),
        _wording(
            (
                "Os partidos têm até lá para registrar candidato e vice.",
                "Até lá, cada partido registra o candidato e o vice.",
                "O registro de candidato e vice vai até essa data.",
            ),
            seed,
            "dek",
        ),
    )


def tickets_closed(
    tickets: list[tuple[str, str, str | None]], days_to_first_round: int, *, seed: Seed
) -> Headline:
    """`tickets` traz, por partido, a sigla, o candidato e o vice (nulo sem vice)."""
    names = [
        f"{candidate} e {vice} pelo {abbr}" if vice else f"{candidate} pelo {abbr}"
        for abbr, candidate, vice in tickets
    ]
    alone = [abbr for abbr, _, vice in tickets if vice is None]
    dek = _wording(
        (
            f"Faltam {days_to_first_round} dias para o 1º turno.",
            f"O 1º turno é daqui a {days_to_first_round} dias.",
            f"Restam {days_to_first_round} dias até o 1º turno.",
        ),
        seed,
        "dek",
    )
    if len(alone) == 1:
        dek = f"O {alone[0]} concorre sem vice. {dek}"
    elif alone:
        dek = f"{_join(alone)} concorrem sem vice. {dek}"
    lead = _wording(
        ("Chapas fechadas", "Estão fechadas as chapas", "Fecham as chapas"), seed
    )
    return Headline(
        NewsType.ELECTION_CALENDAR,
        f"{lead}: {_join(names)}" if names else lead,
        dek,
        party_abbrs=tuple(abbr for abbr, _, _ in tickets),
    )


def election_eve(first_round: date, *, seed: Seed) -> Headline:
    vote = _day_month(first_round)
    return Headline(
        NewsType.ELECTION_CALENDAR,
        _wording(
            (
                f"Eleitores vão às urnas em {vote}",
                f"País vai às urnas em {vote}",
                f"Urnas abrem em {vote} para o 1º turno",
            ),
            seed,
        ),
        _wording(
            (
                "As chapas já fecharam: o resultado sai na apuração do dia.",
                "Com as chapas fechadas, o resultado sai na apuração do dia.",
                "Todas as chapas estão registradas, e a apuração sai no mesmo dia.",
            ),
            seed,
            "dek",
        ),
    )


# Resultado do turno e impeachment


def round_won(
    round_number: int,
    candidate: str,
    abbr: str,
    share: Decimal,
    turned_from: str | None = None,
    *,
    seed: Seed,
) -> Headline:
    """`turned_from` é a sigla de quem liderou o 1º turno e perdeu o 2º: a virada."""
    votes = f"{_share(share)} dos votos válidos"
    if turned_from:
        return Headline(
            NewsType.ELECTION_RESULT,
            _wording(
                (
                    f"Virada: {candidate} ({abbr}) vence o 2º turno, com {votes}",
                    f"{candidate} ({abbr}) vira o jogo e vence o 2º turno, com {votes}",
                    f"Virada no 2º turno: {candidate} ({abbr}) vence, com {votes}",
                ),
                seed,
            ),
            _wording(
                (
                    f"O {turned_from} tinha liderado o 1º turno e perdeu a eleição. "
                    "A posse é em 1º de janeiro.",
                    f"Líder do 1º turno, o {turned_from} perde a eleição. "
                    "A posse é em 1º de janeiro.",
                    f"O {turned_from} saiu na frente no 1º turno, mas perdeu a eleição. "
                    "A posse é em 1º de janeiro.",
                ),
                seed,
                "dek",
            ),
            party_abbrs=(abbr, turned_from),
        )
    title: Wordings = (
        (
            f"{candidate} ({abbr}) vence a eleição no 1º turno, com {votes}",
            f"{candidate} ({abbr}) é eleito no 1º turno, com {votes}",
            f"{candidate} ({abbr}) ganha a eleição já no 1º turno, com {votes}",
        )
        if round_number == 1
        else (
            f"{candidate} ({abbr}) vence o 2º turno, com {votes}",
            f"{candidate} ({abbr}) é eleito no 2º turno, com {votes}",
            f"{candidate} ({abbr}) ganha o 2º turno, com {votes}",
        )
    )
    return Headline(
        NewsType.ELECTION_RESULT,
        _wording(title, seed),
        _wording(
            (
                "A posse é em 1º de janeiro.",
                "A posse acontece em 1º de janeiro.",
                "O novo mandato começa com a posse em 1º de janeiro.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(abbr,),
    )


def runoff_called(
    finalists: list[tuple[str, Decimal]], runoff: date, *, seed: Seed
) -> Headline:
    """`finalists` traz a sigla e a fatia dos válidos de cada finalista, do 1º para o 2º."""
    (first, first_share), (second, second_share) = finalists
    first_votes, second_votes = _share(first_share), _share(second_share)
    vote = _day_month(runoff)
    return Headline(
        NewsType.ELECTION_RESULT,
        _wording(
            (
                f"{first} e {second} vão ao 2º turno",
                f"{first} e {second} disputam o 2º turno",
                f"2º turno será entre {first} e {second}",
            ),
            seed,
        ),
        _wording(
            (
                f"O {first} teve {first_votes} dos válidos e o {second}, "
                f"{second_votes}. A votação é em {vote}.",
                f"O {first} ficou com {first_votes} dos válidos e o {second}, com "
                f"{second_votes}. O 2º turno é em {vote}.",
                f"Com {first_votes} dos válidos, o {first} lidera, seguido do {second}, "
                f"com {second_votes}. A votação é em {vote}.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(first, second),
    )


def impeachment_requested(
    president: str,
    abbr: str | None,
    vote_day: date,
    requester: str | None = None,
    *,
    seed: Seed,
) -> Headline:
    """`requester` é a sigla do partido que pediu; nula quando o piso de aprovação abriu o pedido."""
    party = f" ({abbr})" if abbr else ""
    title: Wordings = (
        (
            f"O {requester} pede o impeachment de {president}{party}",
            f"O {requester} entra com pedido de impeachment contra {president}{party}",
            f"O {requester} quer o impeachment de {president}{party}",
        )
        if requester
        else (
            f"Abre o pedido de impeachment de {president}{party}",
            f"Pedido de impeachment de {president}{party} é aberto",
            f"Aprovação baixa abre pedido de impeachment de {president}{party}",
        )
    )
    vote = f"{vote_day.day:02d}/{vote_day.month:02d}/{vote_day.year}"
    return Headline(
        NewsType.ELECTION_RESULT,
        _wording(title, seed),
        _wording(
            (
                f"A casa vota em {vote}.",
                f"A votação na casa é em {vote}.",
                f"A casa decide em {vote}.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=_abbrs(requester, abbr),
    )


def impeachment_rejected(
    president: str,
    abbr: str | None,
    yes: int,
    no: int,
    requester: str | None = None,
    *,
    seed: Seed,
) -> Headline:
    """`requester` é a sigla do partido que pediu e agora paga o desgaste."""
    party = f" ({abbr})" if abbr else ""
    wear = (
        f" O {requester} perde apoio entre os eleitores que ainda aprovam o presidente."
        if requester
        else ""
    )
    reset = _wording(
        (
            "A contagem de meses abaixo do piso recomeça do zero.",
            "Os meses abaixo do piso deixam de contar, e a contagem recomeça do zero.",
            "O relógio dos meses abaixo do piso volta a zero.",
        ),
        seed,
        "dek",
    )
    return Headline(
        NewsType.ELECTION_RESULT,
        _wording(
            (
                f"Casa rejeita o impeachment de {president}{party} por {no} a {yes}",
                f"Impeachment de {president}{party} é rejeitado pela casa por {no} a {yes}",
                f"{president}{party} se salva do impeachment por {no} a {yes}",
            ),
            seed,
        ),
        f"{reset}{wear}",
        party_abbrs=_abbrs(abbr, requester),
    )


def impeachment(
    president: str,
    abbr: str | None,
    successor: str | None,
    yes: int,
    no: int,
    heir: str | None = None,
    *,
    seed: Seed,
) -> Headline:
    """`heir` é a sigla do partido do computador que assume quando não há vice."""
    party = f" ({abbr})" if abbr else ""
    score = f"{yes} a {no}"
    if successor:
        return Headline(
            NewsType.ELECTION_RESULT,
            _wording(
                (
                    f"Casa tira {president}{party} da Presidência por {score}; {successor} assume",
                    f"{president}{party} sofre impeachment por {score}, e {successor} assume",
                    f"Impeachment aprovado por {score}: {president}{party} sai e {successor} assume",
                ),
                seed,
            ),
            _wording(
                (
                    "A aprovação ficou abaixo do piso por meses seguidos.",
                    "Meses seguidos com a aprovação abaixo do piso selaram o afastamento.",
                    "A aprovação passou meses seguidos abaixo do piso, e a casa agiu.",
                ),
                seed,
                "dek",
            ),
            party_abbrs=_abbrs(abbr),
        )
    if heir:
        return Headline(
            NewsType.ELECTION_RESULT,
            _wording(
                (
                    f"Casa tira {president}{party} da Presidência por {score}; {heir} assume o governo",
                    f"{president}{party} sofre impeachment por {score}, e o {heir} assume o governo",
                    f"Impeachment aprovado por {score}: {president}{party} sai e o {heir} governa",
                ),
                seed,
            ),
            _wording(
                (
                    "Sem vice, governa até o fim do mandato o partido do computador com "
                    f"mais cadeiras ({heir}), propondo medidas pelos eleitores dele.",
                    f"Sem vice, o {heir}, partido do computador com mais cadeiras, governa "
                    "até o fim do mandato e propõe medidas pelos eleitores dele.",
                    "Como não há vice, o partido do computador com mais cadeiras "
                    f"({heir}) assume até o fim do mandato, com medidas voltadas aos "
                    "eleitores dele.",
                ),
                seed,
                "dek",
            ),
            party_abbrs=_abbrs(abbr, heir),
        )
    return Headline(
        NewsType.ELECTION_RESULT,
        _wording(
            (
                f"Casa tira {president}{party} da Presidência por {score}",
                f"{president}{party} sofre impeachment por {score}",
                f"Impeachment aprovado por {score}: {president}{party} deixa a Presidência",
            ),
            seed,
        ),
        _wording(
            (
                "Sem vice, o governo passa ao computador até o fim do mandato.",
                "Como não há vice, o computador governa até o fim do mandato.",
                "O computador assume o governo até o fim do mandato, já que não há vice.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=_abbrs(abbr),
    )


# Posse e medidas


def term_started(
    president: str, abbr: str | None, term_end: date | None, *, seed: Seed
) -> Headline:
    until = f"; o mandato vai até {term_end.year}" if term_end else ""
    return Headline(
        NewsType.TERM_STARTED,
        _wording(
            (
                f"{president} toma posse{until}",
                f"{president} assume a Presidência{until}",
                f"Posse de {president}{until}",
            ),
            seed,
        ),
        _wording(
            (
                f"Presidente pelo {abbr}.",
                f"Chega ao cargo pelo {abbr}.",
                f"A chapa vencedora é do {abbr}.",
            ),
            seed,
            "dek",
        )
        if abbr
        else None,
        party_abbrs=_abbrs(abbr),
    )


def legacy_paid(
    president: str,
    abbr: str | None,
    amount: Decimal,
    average_approval: int,
    *,
    seed: Seed,
) -> Headline:
    """O presidente deixa o cargo ao fim do mandato e recebe o legado que a aprovação rendeu."""
    legacy = format_money(amount)
    return Headline(
        NewsType.TERM_STARTED,
        _wording(
            (
                f"{president} deixa o governo com legado de {legacy}",
                f"{president} encerra o mandato e recebe legado de {legacy}",
                f"Fim de mandato: {president} sai com legado de {legacy}",
            ),
            seed,
        ),
        _wording(
            (
                f"Aprovação média de {average_approval}% durante o mandato.",
                f"O legado vem de uma aprovação média de {average_approval}% no mandato.",
                f"Foram {average_approval}% de aprovação média ao longo do mandato.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=_abbrs(abbr),
    )


def house_seated(
    leader: tuple[str, int],
    seats: int,
    government: tuple[str, int] | None,
    majority: int,
    *,
    seed: Seed,
) -> Headline:
    """O Congresso eleito toma posse: a maior bancada (sigla, cadeiras) e a do governo, se há."""
    abbr, held = leader
    dek = None
    if government is not None:
        party, own = government
        position = "na maioria" if own >= majority else "abaixo da maioria"
        dek = _wording(
            (
                f"A bancada do governo ({party}) começa com {own} cadeiras, {position} "
                f"de {majority}.",
                f"O governo ({party}) começa com {own} cadeiras, {position} de {majority}.",
                f"{party}, partido do governo, abre a legislatura com {own} cadeiras, "
                f"{position} de {majority}.",
            ),
            seed,
            "dek",
        )
    return Headline(
        NewsType.TERM_STARTED,
        _wording(
            (
                f"Novo Congresso toma posse: {abbr} é a maior bancada, com {held} das {seats} cadeiras",
                f"Congresso novo toma posse, com o {abbr} na maior bancada: {held} das {seats} cadeiras",
                f"{abbr} lidera o novo Congresso, com {held} das {seats} cadeiras",
            ),
            seed,
        ),
        dek,
        party_abbrs=_abbrs(abbr, government[0] if government else None),
    )


def measure_proposed(
    president: str, title: str, stake: Decimal | None = None, *, seed: Seed
) -> Headline:
    """A proposta vai à fila; a obra com endereço num setor em que o presidente tem ações conta a fatia dele na carteira."""
    dek = _wording(
        (
            "A medida vai à fila do Congresso.",
            "A proposta entra na fila do Congresso.",
            "A medida segue para a fila de votação do Congresso.",
        ),
        seed,
        "dek",
    )
    if stake:
        dek += f" O presidente tem {percent(stake)} da carteira no setor."
    return Headline(
        NewsType.MEASURE_PROPOSED,
        _wording(
            (
                f"{president} propõe: {title}",
                f"{president} manda ao Congresso: {title}",
                f"Proposta de {president}: {title}",
            ),
            seed,
        ),
        dek,
    )


def measure_withdrawn(president: str, title: str, *, seed: Seed) -> Headline:
    return Headline(
        NewsType.MEASURE_PROPOSED,
        _wording(
            (
                f"{president} retira a proposta: {title}",
                f"{president} recua e retira a proposta: {title}",
                f"Proposta retirada por {president}: {title}",
            ),
            seed,
        ),
    )


def _vote_score(yes: int, no: int, defected: int) -> str:
    return f"{yes} a {no}" + (f", com {defected} que desobedeceram" if defected else "")


def _nothing_changes(score: str, seed: Seed) -> str:
    return _wording(
        (
            f"Placar {score}. Nada muda.",
            f"Placar {score}. Fica tudo como está.",
            f"Placar {score}. A regra atual segue valendo.",
        ),
        seed,
        "dek",
    )


def _in_force(title: str, seed: Seed) -> str:
    return _wording(
        (
            f"Passa a valer: {title}",
            f"Já vale: {title}",
            f"Entra em vigor: {title}",
        ),
        seed,
    )


def measure_voted(
    title: str,
    approved: bool,
    effective: date | None,
    tickers: list[str],
    yes: int,
    no: int,
    defected: int,
    *,
    seed: Seed,
) -> Headline:
    score = _vote_score(yes, no, defected)
    if not approved:
        return Headline(
            NewsType.MEASURE_VOTED,
            _wording(
                (
                    f"Casa rejeita por {no} a {yes}: {title}",
                    f"Casa derruba, por {no} a {yes}: {title}",
                    f"Proposta é rejeitada por {no} a {yes}: {title}",
                ),
                seed,
            ),
            _nothing_changes(score, seed),
            tuple(tickers),
        )
    when = (
        f"Vale a partir de {effective.day:02d}/{effective.month:02d}/{effective.year}."
        if effective
        else None
    )
    lead = _wording(
        (
            f"Placar {score}.",
            f"Votação de {score}.",
            f"A votação fechou em {score}.",
        ),
        seed,
        "dek",
    )
    return Headline(
        NewsType.MEASURE_VOTED,
        _wording(
            (
                f"Casa aprova por {yes} a {no}: {title}",
                f"Aprovada por {yes} a {no}: {title}",
                f"Casa dá o sinal verde por {yes} a {no}: {title}",
            ),
            seed,
        ),
        f"{lead} {when}" if when else lead,
        tuple(tickers),
    )


def _points(peak: Decimal) -> str:
    """Pontos de IPCA em módulo, com a vírgula e a unidade no singular até 1."""
    value = abs(peak)
    unit = "ponto" if value <= 1 else "pontos"
    return f"{precise_number(value)} {unit}"


def spending_voted(
    kind: MeasureKind,
    title: str,
    approved: bool,
    effective: date | None,
    peak: Decimal,
    months_to_peak: int,
    yes: int,
    no: int,
    defected: int,
    *,
    seed: Seed,
) -> Headline:
    """A votação de uma medida de gasto: a manchete diz se o gasto sobe ou cai e o dek, o que a inflação faz."""
    noun = SPENDING_NOUNS[kind]
    raises = peak >= 0
    score = _vote_score(yes, no, defected)
    if not approved:
        what = f"mais gasto com {noun}" if raises else f"o corte em {noun}"
        return Headline(
            NewsType.MEASURE_VOTED,
            _wording(
                (
                    f"Casa barra {what} por {no} a {yes}: {title}",
                    f"Casa derruba {what} por {no} a {yes}: {title}",
                    f"Congresso barra {what} por {no} a {yes}: {title}",
                ),
                seed,
            ),
            _nothing_changes(score, seed),
        )
    what = f"mais gasto com {noun}" if raises else f"corte em {noun}"
    when = (
        f" Vale a partir de {effective.day:02d}/{effective.month:02d}/{effective.year}."
        if effective
        else ""
    )
    direction = "subir" if raises else "ceder"
    points = _points(peak)
    return Headline(
        NewsType.MEASURE_VOTED,
        _wording(
            (
                f"Casa aprova {what} por {yes} a {no}: {title}",
                f"Congresso aprova {what} por {yes} a {no}: {title}",
                f"Casa dá aval a {what} por {yes} a {no}: {title}",
            ),
            seed,
        ),
        _wording(
            (
                f"Placar {score}.{when} O IPCA deve {direction} até {points} "
                f"em {months_to_peak} meses.",
                f"Votação de {score}.{when} A inflação (IPCA) deve {direction} até "
                f"{points} em {months_to_peak} meses.",
                f"A votação fechou em {score}.{when} Em {months_to_peak} meses, o IPCA "
                f"deve {direction} até {points}.",
            ),
            seed,
            "dek",
        ),
    )


def program_event(before: str | None, after: str | None, *, seed: Seed) -> str | None:
    """A manchete do programa que passa a valer: lançado, extinto ou rebatizado; nula quando o nome não muda."""
    if after == before:
        return None
    if before is None:
        return _wording(
            (
                f"Governo lança o {after}",
                f"Governo anuncia o {after}",
                f"Nasce o {after}, novo programa do governo",
            ),
            seed,
        )
    if after is None:
        return _wording(
            (
                f"Governo extingue o {before}",
                f"Governo encerra o {before}",
                f"Fim do {before}: governo extingue o programa",
            ),
            seed,
        )
    return _wording(
        (
            f"Governo rebatiza o {before} como {after}",
            f"O {before} agora se chama {after}",
            f"Governo troca o nome do {before} para {after}",
        ),
        seed,
    )


def spending_in_force(
    title: str,
    peak: Decimal,
    months_to_peak: int,
    program: str | None = None,
    *,
    seed: Seed,
) -> Headline:
    """A medida de gasto que passa a valer; `program` é a manchete do programa, quando o nome muda."""
    direction = "soma" if peak >= 0 else "tira"
    points = _points(peak)
    return Headline(
        NewsType.NAMED_PROGRAM if program else NewsType.MEASURE_VOTED,
        program or _in_force(title, seed),
        _wording(
            (
                f"O efeito na inflação chega cheio em {months_to_peak} meses: a medida "
                f"{direction} até {points} do IPCA em 12 meses.",
                f"A medida {direction} até {points} do IPCA em 12 meses, e o efeito "
                f"chega cheio em {months_to_peak} meses.",
                f"Em {months_to_peak} meses a inflação sente o efeito inteiro: a medida "
                f"{direction} até {points} do IPCA em 12 meses.",
            ),
            seed,
            "dek",
        ),
    )


def measure_in_force(title: str, tickers: list[str], *, seed: Seed) -> Headline:
    return Headline(
        NewsType.MEASURE_VOTED, _in_force(title, seed), None, tuple(tickers)
    )


# Vida dos partidos


def party_founded(founder: str, abbr: str, name: str, *, seed: Seed) -> Headline:
    return Headline(
        NewsType.PARTY_LIFE,
        _wording(
            (
                f"{founder} funda o {abbr}, {name}",
                f"{founder} cria o {abbr}, {name}",
                f"{abbr}, {name}, é fundado por {founder}",
            ),
            seed,
        ),
        party_abbrs=(abbr,),
    )


def donation(donor: str, abbr: str, amount: Decimal, *, seed: Seed) -> Headline:
    money = format_money(amount)
    return Headline(
        NewsType.PARTY_LIFE,
        _wording(
            (
                f"{donor} doa {money} ao {abbr}",
                f"{donor} faz doação de {money} ao {abbr}",
                f"{abbr} recebe {money} de {donor}",
            ),
            seed,
        ),
        _wording(
            (
                "A doação vai para a campanha do 2º turno.",
                "O dinheiro reforça a campanha do 2º turno.",
                "O valor entra na campanha do 2º turno.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(abbr,),
    )


# Rupturas de partido


def expelled(member: str, abbr: str, *, seed: Seed) -> Headline:
    return Headline(
        NewsType.PARTY_RUPTURE,
        _wording(
            (
                f"{member} é expulso do {abbr}",
                f"O {abbr} expulsa {member}",
                f"Expulsão no {abbr}: {member} está fora do partido",
            ),
            seed,
        ),
        party_abbrs=(abbr,),
    )


def federation_formed(
    first: str, second: str, candidate: str, ends: date, *, seed: Seed
) -> Headline:
    """A federação formada: os dois partidos vão numa chapa e numa lista só até o fim do prazo."""
    return Headline(
        NewsType.PARTY_RUPTURE,
        _wording(
            (
                f"{first} e {second} formam federação e vão juntos até {ends.year}",
                f"{first} e {second} se federam e seguem juntos até {ends.year}",
                f"Federação nova: {first} e {second} vão juntos até {ends.year}",
            ),
            seed,
        ),
        _wording(
            (
                f"{candidate} será o candidato dos dois partidos, e o voto de cada um "
                "soma na lista da Câmara.",
                f"{candidate} é o candidato dos dois partidos, e o voto de cada um soma "
                "na lista da Câmara.",
                f"O candidato dos dois partidos é {candidate}, e na Câmara o voto de "
                "cada um soma na mesma lista.",
            ),
            seed,
            "dek",
        ),
    )


def federation_left(leaver: str, other_abbr: str, *, seed: Seed) -> Headline:
    """Quem sai antes do prazo desfaz a federação (`leaver` é o nome do partido, `other_abbr` a sigla do parceiro)."""
    return Headline(
        NewsType.PARTY_RUPTURE,
        _wording(
            (
                f"{leaver} deixa a federação com o {other_abbr} antes do prazo",
                f"{leaver} rompe a federação com o {other_abbr} antes do prazo",
                f"Federação desfeita: {leaver} sai antes do prazo e deixa o {other_abbr}",
            ),
            seed,
        ),
        _wording(
            (
                f"Com a saída, a federação se desfaz. {leaver} fica impedido de se "
                "federar na eleição seguinte e passa a disputar sozinho.",
                f"A federação se desfaz com a saída. {leaver} não pode se federar na "
                "eleição seguinte e disputa sozinho.",
                f"Sem {leaver}, a federação acaba. Na eleição seguinte, {leaver} está "
                "impedido de se federar e disputa sozinho.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(other_abbr,),
    )


def deal_made(
    president: str,
    ally_abbr: str,
    ally_seats: int,
    base_seats: int,
    majority: int,
    end: date,
    sector: str | None = None,
    *,
    seed: Seed,
) -> Headline:
    """O acordo de apoio fechado: o aliado entra na base e a manchete diz em que pé a base fica e, se a emenda tem endereço, para que setor ela vai."""
    position = "na maioria" if base_seats >= majority else "abaixo da maioria"
    where = f" A emenda vai para {sector}." if sector else ""
    until = f"{end.day:02d}/{end.month:02d}/{end.year}"
    return Headline(
        NewsType.PARTY_LIFE,
        _wording(
            (
                f"{ally_abbr} entra na base do governo de {president}",
                f"{ally_abbr} fecha acordo e entra na base de {president}",
                f"Governo de {president} ganha o apoio do {ally_abbr}",
            ),
            seed,
        ),
        _wording(
            (
                f"São {ally_seats} cadeiras: a base vai a {base_seats}, {position} de "
                f"{majority}. O acordo vale até {until}, com emendas pagas todo "
                f"mês.{where}",
                f"A base vai a {base_seats} cadeiras com as {ally_seats} do {ally_abbr}, "
                f"{position} de {majority}. O acordo vale até {until}, e as emendas são "
                f"pagas todo mês.{where}",
                f"O acordo dura até {until} e traz {ally_seats} cadeiras: a base chega a "
                f"{base_seats}, {position} de {majority}. As emendas saem todo "
                f"mês.{where}",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(ally_abbr,),
    )


def deal_broken(
    president: str,
    government_abbr: str,
    ally_abbr: str,
    by_ally: bool,
    oriented_no: bool,
    ally_seats: int,
    base_seats: int,
    majority: int,
    groups: list[VoterGroup],
    *,
    seed: Seed,
) -> Headline:
    """O acordo de apoio acabou na quebra: o aliado rompeu (ou orientou Não) ou o governo cortou as emendas."""
    title: Wordings
    if by_ally and oriented_no:
        title = (
            f"{ally_abbr} orienta Não ao governo e rompe o acordo",
            f"{ally_abbr} rompe o acordo e manda a bancada votar Não ao governo",
            f"Rompimento: {ally_abbr} orienta Não ao governo e desfaz o acordo",
        )
    elif by_ally:
        title = (
            f"{ally_abbr} deixa a base do governo de {president}",
            f"{ally_abbr} rompe com o governo de {president} e deixa a base",
            f"Base do governo de {president} perde o {ally_abbr}",
        )
    else:
        title = (
            f"{president} corta as emendas do {ally_abbr}",
            f"Governo de {president} corta as emendas do {ally_abbr} e rompe o acordo",
            f"Sem emendas: {president} rompe o acordo com o {ally_abbr}",
        )
    position = (
        f"A base cai para {base_seats} cadeiras, "
        + ("abaixo" if base_seats < majority else "ainda acima")
        + f" da maioria de {majority}."
    )
    loser = "o governo" if by_ally else ally_abbr
    pain = (
        f" A quebra pesa para {loser} {_among(groups[0])}"
        + (f" e {GROUP_NAMES[groups[1]]}" if len(groups) > 1 else "")
        + "."
        if groups
        else ""
    )
    lead = _wording(
        (
            f"São {ally_seats} cadeiras que mudam de lado.",
            f"{ally_seats} cadeiras mudam de lado.",
            f"A mudança de lado leva {ally_seats} cadeiras.",
        ),
        seed,
        "dek",
    )
    return Headline(
        NewsType.PARTY_RUPTURE,
        _wording(title, seed),
        f"{lead} {position}{pain}",
        party_abbrs=(ally_abbr,),
    )


def deal_left(
    president: str,
    ally_abbr: str,
    ally_seats: int,
    base_seats: int,
    majority: int,
    *,
    seed: Seed,
) -> Headline:
    """A bancada deixa a base porque o governo fraco não aceitou pagar mais; não há quebra nem culpado."""
    position = "abaixo" if base_seats < majority else "ainda acima"
    return Headline(
        NewsType.PARTY_RUPTURE,
        _wording(
            (
                f"O {ally_abbr} deixa a base do governo",
                f"{ally_abbr} abandona a base do governo",
                f"Base do governo perde o {ally_abbr}",
            ),
            seed,
        ),
        _wording(
            (
                f"Com a aprovação de {president} em baixa, a bancada não segue apoiando "
                f"sem o reajuste que cobrou. São {ally_seats} cadeiras: a base cai para "
                f"{base_seats}, {position} da maioria de {majority}.",
                f"A aprovação de {president} está em baixa e a bancada cobrou um reajuste "
                f"que não veio, então sai. São {ally_seats} cadeiras: a base cai para "
                f"{base_seats}, {position} da maioria de {majority}.",
                f"Sem o reajuste que cobrou e com a aprovação de {president} em baixa, a "
                f"bancada deixa de apoiar. Saem {ally_seats} cadeiras: a base cai para "
                f"{base_seats}, {position} da maioria de {majority}.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(ally_abbr,),
    )


def deals_ended(abbrs: list[str], new_congress: bool, *, seed: Seed) -> Headline:
    cause = "com a posse do novo Congresso" if new_congress else "pelo prazo"
    return Headline(
        NewsType.PARTY_LIFE,
        _wording(
            (
                f"Acabam os acordos de apoio com {_join(abbrs)}",
                f"Terminam os acordos de apoio com {_join(abbrs)}",
                f"Fim dos acordos de apoio com {_join(abbrs)}",
            ),
            seed,
        ),
        _wording(
            (
                f"Os acordos terminaram {cause}, e as emendas deixam de ser pagas.",
                f"Acordos encerrados {cause}: as emendas deixam de ser pagas.",
                f"As emendas deixam de ser pagas: os acordos terminaram {cause}.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=tuple(abbrs),
    )


# Campanha

VIRAL_DEKS: Wordings = (
    "O vídeo passa de um milhão de visualizações em um dia.",
    "A hashtag da campanha fica entre as mais comentadas do país.",
    "Até adversários comentam o momento, que circula o dia todo.",
)
DISASTER_DEKS: Wordings = (
    "A fala circulou o dia todo e a campanha teve de se explicar.",
    "Vaias e uma resposta atravessada viram o assunto do dia.",
    "A equipe pediu desculpas, mas o vídeo já tinha se espalhado.",
)
ATTACK_DEKS: Wordings = (
    "A peça acusa o adversário de abandonar o grupo.",
    "A propaganda compara as promessas do rival com o que ele fez.",
    "O material circula nas redes e nos grupos de mensagem.",
)
BACKFIRE_DEKS: Wordings = (
    "A peça foi tirada do ar depois das críticas.",
    "O ataque virou piada nas redes e o alvo saiu fortalecido.",
    "Até aliados criticaram o tom da propaganda.",
)

ACTION_NOUN = {
    CampaignActionKind.EVENT: "Evento",
    CampaignActionKind.RALLY: "Comício",
}


def campaign_action(
    kind: CampaignActionKind,
    band: DiceBand,
    abbr: str,
    group: VoterGroup | None,
    rival_abbr: str | None,
    *,
    seed: Seed,
) -> Headline | None:
    """Sai no jornal a ação que viraliza ou dá errado e todo ataque; o resto fica no histórico do partido."""
    if kind is CampaignActionKind.ATTACK and group is not None and rival_abbr:
        among = _among(group)
        if band is DiceBand.DISASTER:
            title: Wordings = (
                f"Ataque do {abbr} ao {rival_abbr} sai pela culatra {among}",
                f"{abbr} se dá mal ao atacar o {rival_abbr} {among}",
                f"Ataque ao {rival_abbr} vira contra o {abbr} {among}",
            )
            deks = BACKFIRE_DEKS
        elif band is DiceBand.VIRAL:
            title = (
                f"Ataque do {abbr} ao {rival_abbr} viraliza {among}",
                f"{abbr} acerta o {rival_abbr} e o ataque viraliza {among}",
                f"Ataque do {abbr} ao {rival_abbr} faz barulho {among}",
            )
            deks = VIRAL_DEKS
        else:
            title = (
                f"{abbr} parte para o ataque contra o {rival_abbr} {among}",
                f"{abbr} ataca o {rival_abbr} {among}",
                f"Campanha do {abbr} mira o {rival_abbr} {among}",
            )
            deks = ATTACK_DEKS
        return Headline(
            NewsType.CAMPAIGN_ACTION,
            _wording(title, seed),
            _wording(deks, seed, "dek"),
            party_abbrs=(abbr, rival_abbr),
        )
    if band is DiceBand.VIRAL:
        title = (
            (
                f"Propaganda do {abbr} na TV viraliza",
                f"Propaganda do {abbr} na TV vira sucesso nas redes",
                f"Anúncio do {abbr} na TV toma conta das redes",
            )
            if group is None or kind is CampaignActionKind.TV
            else (
                f"{ACTION_NOUN[kind]} do {abbr} {_with(group)} viraliza",
                f"{ACTION_NOUN[kind]} do {abbr} {_with(group)} toma conta das redes",
                f"{ACTION_NOUN[kind]} do {abbr} {_with(group)} vira assunto do dia",
            )
        )
        return Headline(
            NewsType.CAMPAIGN_ACTION,
            _wording(title, seed),
            _wording(VIRAL_DEKS, seed, "dek"),
            party_abbrs=(abbr,),
        )
    if band is DiceBand.DISASTER:
        title = (
            (
                f"Propaganda do {abbr} na TV vira polêmica",
                f"Propaganda do {abbr} na TV é alvo de críticas",
                f"Anúncio do {abbr} na TV gera polêmica",
            )
            if group is None or kind is CampaignActionKind.TV
            else (
                f"Candidato do {abbr} se envolve em polêmica no "
                f"{ACTION_NOUN[kind].lower()} {_with(group)}",
                f"{ACTION_NOUN[kind]} do {abbr} {_with(group)} termina em polêmica",
                f"Candidato do {abbr} causa polêmica no "
                f"{ACTION_NOUN[kind].lower()} {_with(group)}",
            )
        )
        return Headline(
            NewsType.CAMPAIGN_ACTION,
            _wording(title, seed),
            _wording(DISASTER_DEKS, seed, "dek"),
            party_abbrs=(abbr,),
        )
    return None


def promises_set(
    abbr: str,
    count: int,
    had_promises: bool,
    retreated: list[str] | None = None,
    *,
    seed: Seed,
) -> Headline:
    """`retreated` traz as promessas já anunciadas que a nova lista abandonou (retirou, trocou ou baixou)."""
    withdrawn: Wordings = (
        f"{abbr} retira as promessas de campanha",
        f"{abbr} desiste das promessas de campanha",
        f"{abbr} abre mão das promessas de campanha",
    )
    if retreated:
        dek = _wording(
            (
                f"Deixou de prometer: {_join(retreated)}. Voltar atrás soma rejeição "
                "entre quem queria a medida.",
                f"Saem da lista: {_join(retreated)}. Voltar atrás soma rejeição entre "
                "quem queria a medida.",
                f"Abandonou: {_join(retreated)}. A rejeição sobe entre quem queria a "
                "medida.",
            ),
            seed,
            "dek",
        )
        if count == 0:
            return Headline(
                NewsType.CAMPAIGN, _wording(withdrawn, seed), dek, party_abbrs=(abbr,)
            )
        what = "uma promessa" if len(retreated) == 1 else f"{len(retreated)} promessas"
        text = _wording(
            (
                f"{abbr} volta atrás em {what} de campanha",
                f"{abbr} recua em {what} de campanha",
                f"{abbr} abandona {what} de campanha",
            ),
            seed,
        )
        return Headline(NewsType.CAMPAIGN, text, dek, party_abbrs=(abbr,))
    if count == 0:
        return Headline(
            NewsType.CAMPAIGN, _wording(withdrawn, seed), party_abbrs=(abbr,)
        )
    noun = "promessa" if count == 1 else "promessas"
    title: Wordings = (
        (
            f"{abbr} revê as promessas de campanha",
            f"{abbr} refaz a lista de promessas de campanha",
            f"{abbr} atualiza as promessas de campanha",
        )
        if had_promises
        else (
            f"{abbr} anuncia as promessas de campanha",
            f"{abbr} apresenta as promessas de campanha",
            f"{abbr} divulga as promessas de campanha",
        )
    )
    return Headline(
        NewsType.CAMPAIGN,
        _wording(title, seed),
        _wording(
            (
                f"São {count} {noun}, cobradas no fim do mandato se a chapa vencer.",
                f"A lista tem {count} {noun}, cobradas no fim do mandato se a chapa vencer.",
                f"Se a chapa vencer, a cobrança vem no fim do mandato: {count} {noun}.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(abbr,),
    )


def promises_settled(abbr: str, kept: int, total: int, *, seed: Seed) -> Headline:
    return Headline(
        NewsType.CAMPAIGN,
        _wording(
            (
                f"Fim do mandato: o {abbr} cumpre {kept} de {total} promessas",
                f"O {abbr} chega ao fim do mandato com {kept} de {total} promessas cumpridas",
                f"Balanço do mandato: {abbr} cumpre {kept} das {total} promessas",
            ),
            seed,
        ),
        _wording(
            (
                "Promessa cumprida soma afinidade; descumprida soma rejeição.",
                "Quem cumpre a promessa ganha afinidade; quem descumpre, rejeição.",
                "O cumprimento soma afinidade e o descumprimento soma rejeição.",
            ),
            seed,
            "dek",
        ),
        party_abbrs=(abbr,),
    )


def endorsement(abbr: str, endorsed_abbr: str | None, *, seed: Seed) -> Headline:
    if endorsed_abbr is None:
        return Headline(
            NewsType.CAMPAIGN,
            _wording(
                (
                    f"{abbr} fica neutro no 2º turno",
                    f"{abbr} não apoia ninguém no 2º turno",
                    f"{abbr} decide ficar neutro no 2º turno",
                ),
                seed,
            ),
            party_abbrs=(abbr,),
        )
    return Headline(
        NewsType.CAMPAIGN,
        _wording(
            (
                f"{abbr} declara apoio ao {endorsed_abbr} no 2º turno",
                f"{abbr} apoia o {endorsed_abbr} no 2º turno",
                f"{abbr} anuncia apoio ao {endorsed_abbr} no 2º turno",
            ),
            seed,
        ),
        party_abbrs=(abbr, endorsed_abbr),
    )
