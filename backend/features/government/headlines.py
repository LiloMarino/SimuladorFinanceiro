"""
As manchetes da política no jornal da partida. Cada uma conta o fato para a sala inteira,
na terceira pessoa; os números de campanha (dado, pontos de apoio) ficam com o partido.
"""

from datetime import date
from decimal import Decimal

from backend.core.enum import CampaignActionKind, DiceBand, NewsType, VoterGroup
from backend.core.utils import format_money
from backend.features.government.measures import MONTHS, number
from backend.features.notifications.news import Headline

GROUP_NAMES: dict[VoterGroup, str] = {
    VoterGroup.INVESTORS: "investidores",
    VoterGroup.ENTREPRENEURS: "empreendedores",
    VoterGroup.FORMAL_WORKERS: "trabalhadores com carteira",
    VoterGroup.PUBLIC_SERVANTS: "servidores",
    VoterGroup.RETIREES: "aposentados",
    VoterGroup.WELFARE: "quem depende de auxílio",
}

HUNDRED = Decimal(100)


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


def _join(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} e {items[-1]}"


# Calendário da eleição


def campaign_opened(first_round: date, ticket_deadline: date) -> Headline:
    return Headline(
        NewsType.ELECTION_CALENDAR,
        f"Começa a campanha para a eleição de {_month_year(first_round)}",
        f"As chapas fecham em {_day_month(ticket_deadline)} e o 1º turno é em "
        f"{_day_month(first_round)}. Já dá para fundar partido, fazer comício, evento "
        "e propaganda na TV.",
    )


def tickets_closing(ticket_deadline: date) -> Headline:
    return Headline(
        NewsType.ELECTION_CALENDAR,
        f"Chapas fecham em {_day_month(ticket_deadline)}",
        "Os partidos têm até lá para registrar candidato e vice.",
    )


def tickets_closed(
    tickets: list[tuple[str, str, str | None]], days_to_first_round: int
) -> Headline:
    """`tickets` traz, por partido, a sigla, o candidato e o vice (nulo sem vice)."""
    names = [
        f"{candidate} e {vice} pelo {abbr}" if vice else f"{candidate} pelo {abbr}"
        for abbr, candidate, vice in tickets
    ]
    alone = [abbr for abbr, _, vice in tickets if vice is None]
    dek = f"Faltam {days_to_first_round} dias para o 1º turno."
    if len(alone) == 1:
        dek = f"O {alone[0]} concorre sem vice. {dek}"
    elif alone:
        dek = f"{_join(alone)} concorrem sem vice. {dek}"
    return Headline(
        NewsType.ELECTION_CALENDAR,
        f"Chapas fechadas: {_join(names)}" if names else "Chapas fechadas",
        dek,
    )


def election_eve(first_round: date) -> Headline:
    return Headline(
        NewsType.ELECTION_CALENDAR,
        f"Eleitores vão às urnas em {_day_month(first_round)}",
        "As chapas já fecharam: o resultado sai na apuração do dia.",
    )


# Resultado do turno e impeachment


def round_won(round_number: int, candidate: str, abbr: str, share: Decimal) -> Headline:
    where = "no 1º turno" if round_number == 1 else "o 2º turno"
    verb = "vence a eleição" if round_number == 1 else "vence"
    return Headline(
        NewsType.ELECTION_RESULT,
        f"{candidate} ({abbr}) {verb} {where}, com {_share(share)} dos votos válidos",
        "A posse é em 1º de janeiro.",
    )


def runoff_called(finalists: list[tuple[str, Decimal]], runoff: date) -> Headline:
    """`finalists` traz a sigla e a fatia dos válidos de cada finalista, do 1º para o 2º."""
    (first, first_share), (second, second_share) = finalists
    return Headline(
        NewsType.ELECTION_RESULT,
        f"{first} e {second} vão ao 2º turno",
        f"O {first} teve {_share(first_share)} dos válidos e o {second}, "
        f"{_share(second_share)}. A votação é em {_day_month(runoff)}.",
    )


def impeachment_requested(president: str, abbr: str | None, vote_day: date) -> Headline:
    party = f" ({abbr})" if abbr else ""
    return Headline(
        NewsType.ELECTION_RESULT,
        f"Abre o pedido de impeachment de {president}{party}",
        f"A casa vota em {vote_day.day:02d}/{vote_day.month:02d}/{vote_day.year}.",
    )


def impeachment_rejected(
    president: str, abbr: str | None, yes: int, no: int
) -> Headline:
    party = f" ({abbr})" if abbr else ""
    return Headline(
        NewsType.ELECTION_RESULT,
        f"Casa rejeita o impeachment de {president}{party} por {no} a {yes}",
        "A contagem de meses abaixo do piso recomeça do zero.",
    )


def impeachment(
    president: str, abbr: str | None, successor: str | None, yes: int, no: int
) -> Headline:
    party = f" ({abbr})" if abbr else ""
    if successor:
        return Headline(
            NewsType.ELECTION_RESULT,
            f"Casa tira {president}{party} da Presidência por {yes} a {no}; {successor} assume",
            "A aprovação ficou abaixo do piso por meses seguidos.",
        )
    return Headline(
        NewsType.ELECTION_RESULT,
        f"Casa tira {president}{party} da Presidência por {yes} a {no}",
        "Sem vice, o governo passa ao computador até o fim do mandato.",
    )


# Posse e medidas


def term_started(president: str, abbr: str | None, term_end: date | None) -> Headline:
    until = f"; o mandato vai até {term_end.year}" if term_end else ""
    return Headline(
        NewsType.TERM_STARTED,
        f"{president} toma posse{until}",
        f"Presidente pelo {abbr}." if abbr else None,
    )


def measure_proposed(president: str, title: str) -> Headline:
    return Headline(
        NewsType.MEASURE_PROPOSED,
        f"{president} propõe: {title}",
        "A medida vai à fila do Congresso.",
    )


def measure_withdrawn(president: str, title: str) -> Headline:
    return Headline(
        NewsType.MEASURE_PROPOSED, f"{president} retira a proposta: {title}"
    )


def measure_voted(
    title: str,
    approved: bool,
    effective: date | None,
    tickers: list[str],
    yes: int,
    no: int,
    defected: int,
) -> Headline:
    score = f"{yes} a {no}" + (
        f", com {defected} que desobedeceram" if defected else ""
    )
    if not approved:
        return Headline(
            NewsType.MEASURE_VOTED,
            f"Casa rejeita por {no} a {yes}: {title}",
            f"Placar {score}. Nada muda.",
            tuple(tickers),
        )
    when = (
        f"Vale a partir de {effective.day:02d}/{effective.month:02d}/{effective.year}."
        if effective
        else None
    )
    return Headline(
        NewsType.MEASURE_VOTED,
        f"Casa aprova por {yes} a {no}: {title}",
        f"Placar {score}. {when}" if when else f"Placar {score}.",
        tuple(tickers),
    )


def measure_in_force(title: str, tickers: list[str]) -> Headline:
    return Headline(
        NewsType.MEASURE_VOTED, f"Passa a valer: {title}", None, tuple(tickers)
    )


# Vida dos partidos


def party_founded(founder: str, abbr: str, name: str) -> Headline:
    return Headline(NewsType.PARTY_LIFE, f"{founder} funda o {abbr}, {name}")


def donation(donor: str, abbr: str, amount: Decimal) -> Headline:
    return Headline(
        NewsType.PARTY_LIFE,
        f"{donor} doa {format_money(amount)} ao {abbr}",
        "A doação vai para a campanha do 2º turno.",
    )


def expelled(member: str, abbr: str) -> Headline:
    return Headline(NewsType.PARTY_LIFE, f"{member} é expulso do {abbr}")


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
) -> Headline:
    """O acordo de apoio acabou na quebra: o aliado rompeu (ou orientou Não) ou o governo cortou as emendas."""
    if by_ally and oriented_no:
        title = f"{ally_abbr} orienta Não ao governo e rompe o acordo"
    elif by_ally:
        title = f"{ally_abbr} deixa a base do governo de {president}"
    else:
        title = f"{president} corta as emendas do {ally_abbr}"
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
    return Headline(
        NewsType.PARTY_LIFE,
        title,
        f"São {ally_seats} cadeiras que mudam de lado. {position}{pain}",
    )


def deals_ended(abbrs: list[str], new_congress: bool) -> Headline:
    cause = "com a posse do novo Congresso" if new_congress else "pelo prazo"
    return Headline(
        NewsType.PARTY_LIFE,
        f"Acabam os acordos de apoio com {_join(abbrs)}",
        f"Os acordos terminaram {cause}, e as emendas deixam de ser pagas.",
    )


# Campanha

# As linhas de apoio de cada tom; a ação escolhe uma pelo número dela
VIRAL_DEKS = (
    "O vídeo passa de um milhão de visualizações em um dia.",
    "A hashtag da campanha fica entre as mais comentadas do país.",
    "Até adversários comentam o momento, que circula o dia todo.",
)
DISASTER_DEKS = (
    "A fala circulou o dia todo e a campanha teve de se explicar.",
    "Vaias e uma resposta atravessada viram o assunto do dia.",
    "A equipe pediu desculpas, mas o vídeo já tinha se espalhado.",
)
ATTACK_DEKS = (
    "A peça acusa o adversário de abandonar o grupo.",
    "A propaganda compara as promessas do rival com o que ele fez.",
    "O material circula nas redes e nos grupos de mensagem.",
)
BACKFIRE_DEKS = (
    "A peça foi tirada do ar depois das críticas.",
    "O ataque virou piada nas redes e o alvo saiu fortalecido.",
    "Até aliados criticaram o tom da propaganda.",
)

ACTION_NOUN = {
    CampaignActionKind.EVENT: "Evento",
    CampaignActionKind.RALLY: "Comício",
}


def campaign_action(
    action_id: int,
    kind: CampaignActionKind,
    band: DiceBand,
    abbr: str,
    group: VoterGroup | None,
    rival_abbr: str | None,
) -> Headline | None:
    """Sai no jornal a ação que viraliza ou dá errado e todo ataque; o resto fica no histórico do partido."""
    if kind is CampaignActionKind.ATTACK and group is not None and rival_abbr:
        if band is DiceBand.DISASTER:
            return Headline(
                NewsType.CAMPAIGN,
                f"Ataque do {abbr} ao {rival_abbr} sai pela culatra {_among(group)}",
                BACKFIRE_DEKS[action_id % len(BACKFIRE_DEKS)],
            )
        if band is DiceBand.VIRAL:
            return Headline(
                NewsType.CAMPAIGN,
                f"Ataque do {abbr} ao {rival_abbr} viraliza {_among(group)}",
                VIRAL_DEKS[action_id % len(VIRAL_DEKS)],
            )
        return Headline(
            NewsType.CAMPAIGN,
            f"{abbr} parte para o ataque contra o {rival_abbr} {_among(group)}",
            ATTACK_DEKS[action_id % len(ATTACK_DEKS)],
        )
    if band is DiceBand.VIRAL:
        text = (
            f"Propaganda do {abbr} na TV viraliza"
            if kind is CampaignActionKind.TV or group is None
            else f"{ACTION_NOUN[kind]} do {abbr} {_with(group)} viraliza"
        )
        return Headline(
            NewsType.CAMPAIGN, text, VIRAL_DEKS[action_id % len(VIRAL_DEKS)]
        )
    if band is DiceBand.DISASTER:
        text = (
            f"Propaganda do {abbr} na TV vira polêmica"
            if kind is CampaignActionKind.TV or group is None
            else f"Candidato do {abbr} se envolve em polêmica no "
            f"{ACTION_NOUN[kind].lower()} {_with(group)}"
        )
        return Headline(
            NewsType.CAMPAIGN, text, DISASTER_DEKS[action_id % len(DISASTER_DEKS)]
        )
    return None


def promises_set(abbr: str, count: int, had_promises: bool) -> Headline:
    if count == 0:
        return Headline(NewsType.CAMPAIGN, f"{abbr} retira as promessas de campanha")
    noun = "promessa" if count == 1 else "promessas"
    verb = "revê" if had_promises else "anuncia"
    return Headline(
        NewsType.CAMPAIGN,
        f"{abbr} {verb} as promessas de campanha",
        f"São {count} {noun}, cobradas no fim do mandato se a chapa vencer.",
    )


def promises_settled(abbr: str, kept: int, total: int) -> Headline:
    return Headline(
        NewsType.CAMPAIGN,
        f"Fim do mandato: o {abbr} cumpre {kept} de {total} promessas",
        "Promessa cumprida soma afinidade; descumprida soma rejeição.",
    )


def endorsement(abbr: str, endorsed_abbr: str | None) -> Headline:
    if endorsed_abbr is None:
        return Headline(NewsType.CAMPAIGN, f"{abbr} fica neutro no 2º turno")
    return Headline(
        NewsType.CAMPAIGN, f"{abbr} declara apoio ao {endorsed_abbr} no 2º turno"
    )
