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


def _join(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} e {items[-1]}"


# Calendário da eleição


def campaign_opened(first_round: date, ticket_deadline: date) -> Headline:
    return Headline(
        NewsType.CAMPAIGN_OPENED,
        f"Começa a campanha para a eleição de {_month_year(first_round)}",
        f"As chapas fecham em {_day_month(ticket_deadline)} e o 1º turno é em "
        f"{_day_month(first_round)}. Já dá para inscrever a chapa, fazer comício, evento "
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
        party_abbrs=tuple(abbr for abbr, _, _ in tickets),
    )


def election_eve(first_round: date) -> Headline:
    return Headline(
        NewsType.ELECTION_CALENDAR,
        f"Eleitores vão às urnas em {_day_month(first_round)}",
        "As chapas já fecharam: o resultado sai na apuração do dia.",
    )


# Resultado do turno e impeachment


def round_won(
    round_number: int,
    candidate: str,
    abbr: str,
    share: Decimal,
    turned_from: str | None = None,
) -> Headline:
    """`turned_from` é a sigla de quem liderou o 1º turno e perdeu o 2º: a virada."""
    where = "no 1º turno" if round_number == 1 else "o 2º turno"
    verb = "vence a eleição" if round_number == 1 else "vence"
    if turned_from:
        return Headline(
            NewsType.ELECTION_RESULT,
            f"Virada: {candidate} ({abbr}) vence o 2º turno, com {_share(share)} dos votos válidos",
            f"O {turned_from} tinha liderado o 1º turno e perdeu a eleição. "
            "A posse é em 1º de janeiro.",
            party_abbrs=(abbr, turned_from),
        )
    return Headline(
        NewsType.ELECTION_RESULT,
        f"{candidate} ({abbr}) {verb} {where}, com {_share(share)} dos votos válidos",
        "A posse é em 1º de janeiro.",
        party_abbrs=(abbr,),
    )


def runoff_called(finalists: list[tuple[str, Decimal]], runoff: date) -> Headline:
    """`finalists` traz a sigla e a fatia dos válidos de cada finalista, do 1º para o 2º."""
    (first, first_share), (second, second_share) = finalists
    return Headline(
        NewsType.ELECTION_RESULT,
        f"{first} e {second} vão ao 2º turno",
        f"O {first} teve {_share(first_share)} dos válidos e o {second}, "
        f"{_share(second_share)}. A votação é em {_day_month(runoff)}.",
        party_abbrs=(first, second),
    )


def impeachment_requested(
    president: str, abbr: str | None, vote_day: date, requester: str | None = None
) -> Headline:
    """`requester` é a sigla do partido que pediu; nula quando o piso de aprovação abriu o pedido."""
    party = f" ({abbr})" if abbr else ""
    title = (
        f"O {requester} pede o impeachment de {president}{party}"
        if requester
        else f"Abre o pedido de impeachment de {president}{party}"
    )
    return Headline(
        NewsType.ELECTION_RESULT,
        title,
        f"A casa vota em {vote_day.day:02d}/{vote_day.month:02d}/{vote_day.year}.",
        party_abbrs=_abbrs(requester, abbr),
    )


def impeachment_rejected(
    president: str,
    abbr: str | None,
    yes: int,
    no: int,
    requester: str | None = None,
) -> Headline:
    """`requester` é a sigla do partido que pediu e agora paga o desgaste."""
    party = f" ({abbr})" if abbr else ""
    wear = (
        f" O {requester} perde apoio entre os eleitores que ainda aprovam o presidente."
        if requester
        else ""
    )
    return Headline(
        NewsType.ELECTION_RESULT,
        f"Casa rejeita o impeachment de {president}{party} por {no} a {yes}",
        f"A contagem de meses abaixo do piso recomeça do zero.{wear}",
        party_abbrs=_abbrs(abbr, requester),
    )


def impeachment(
    president: str,
    abbr: str | None,
    successor: str | None,
    yes: int,
    no: int,
    heir: str | None = None,
) -> Headline:
    """`heir` é a sigla do partido do computador que assume quando não há vice."""
    party = f" ({abbr})" if abbr else ""
    if successor:
        return Headline(
            NewsType.ELECTION_RESULT,
            f"Casa tira {president}{party} da Presidência por {yes} a {no}; {successor} assume",
            "A aprovação ficou abaixo do piso por meses seguidos.",
            party_abbrs=_abbrs(abbr),
        )
    if heir:
        return Headline(
            NewsType.ELECTION_RESULT,
            f"Casa tira {president}{party} da Presidência por {yes} a {no}; {heir} assume o governo",
            f"Sem vice, governa até o fim do mandato o partido do computador com mais cadeiras ({heir}), propondo medidas pelos eleitores dele.",
            party_abbrs=_abbrs(abbr, heir),
        )
    return Headline(
        NewsType.ELECTION_RESULT,
        f"Casa tira {president}{party} da Presidência por {yes} a {no}",
        "Sem vice, o governo passa ao computador até o fim do mandato.",
        party_abbrs=_abbrs(abbr),
    )


# Posse e medidas


def term_started(president: str, abbr: str | None, term_end: date | None) -> Headline:
    until = f"; o mandato vai até {term_end.year}" if term_end else ""
    return Headline(
        NewsType.TERM_STARTED,
        f"{president} toma posse{until}",
        f"Presidente pelo {abbr}." if abbr else None,
        party_abbrs=_abbrs(abbr),
    )


def legacy_paid(
    president: str, abbr: str | None, amount: Decimal, average_approval: int
) -> Headline:
    """O presidente deixa o cargo ao fim do mandato e recebe o legado que a aprovação rendeu."""
    return Headline(
        NewsType.TERM_STARTED,
        f"{president} deixa o governo com legado de {format_money(amount)}",
        f"Aprovação média de {average_approval}% durante o mandato.",
        party_abbrs=_abbrs(abbr),
    )


def house_seated(
    leader: tuple[str, int],
    seats: int,
    government: tuple[str, int] | None,
    majority: int,
) -> Headline:
    """O Congresso eleito toma posse: a maior bancada (sigla, cadeiras) e a do governo, se há."""
    abbr, held = leader
    dek = None
    if government is not None:
        party, own = government
        position = "na maioria" if own >= majority else "abaixo da maioria"
        dek = (
            f"A bancada do governo ({party}) começa com {own} cadeiras, {position} "
            f"de {majority}."
        )
    return Headline(
        NewsType.TERM_STARTED,
        f"Novo Congresso toma posse: {abbr} é a maior bancada, com {held} das {seats} cadeiras",
        dek,
        party_abbrs=_abbrs(abbr, government[0] if government else None),
    )


def measure_proposed(
    president: str, title: str, stake: Decimal | None = None
) -> Headline:
    """A proposta vai à fila; a obra com endereço num setor em que o presidente tem ações conta a fatia dele na carteira."""
    dek = "A medida vai à fila do Congresso."
    if stake:
        dek += f" O presidente tem {percent(stake)} da carteira no setor."
    return Headline(NewsType.MEASURE_PROPOSED, f"{president} propõe: {title}", dek)


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
) -> Headline:
    """A votação de uma medida de gasto: a manchete diz se o gasto sobe ou cai e o dek, o que a inflação faz."""
    noun = SPENDING_NOUNS[kind]
    raises = peak >= 0
    score = f"{yes} a {no}" + (
        f", com {defected} que desobedeceram" if defected else ""
    )
    if not approved:
        what = f"mais gasto com {noun}" if raises else f"o corte em {noun}"
        return Headline(
            NewsType.MEASURE_VOTED,
            f"Casa barra {what} por {no} a {yes}: {title}",
            f"Placar {score}. Nada muda.",
        )
    what = f"mais gasto com {noun}" if raises else f"corte em {noun}"
    when = (
        f" Vale a partir de {effective.day:02d}/{effective.month:02d}/{effective.year}."
        if effective
        else ""
    )
    direction = "subir" if raises else "ceder"
    return Headline(
        NewsType.MEASURE_VOTED,
        f"Casa aprova {what} por {yes} a {no}: {title}",
        f"Placar {score}.{when} O IPCA deve {direction} até {_points(peak)} "
        f"em {months_to_peak} meses.",
    )


def program_event(before: str | None, after: str | None) -> str | None:
    """A manchete do programa que passa a valer: lançado, extinto ou rebatizado; nula quando o nome não muda."""
    if after == before:
        return None
    if before is None:
        return f"Governo lança o {after}"
    if after is None:
        return f"Governo extingue o {before}"
    return f"Governo rebatiza o {before} como {after}"


def spending_in_force(
    title: str, peak: Decimal, months_to_peak: int, program: str | None = None
) -> Headline:
    """A medida de gasto que passa a valer; `program` é a manchete do programa, quando o nome muda."""
    direction = "soma" if peak >= 0 else "tira"
    return Headline(
        NewsType.MEASURE_VOTED,
        program or f"Passa a valer: {title}",
        f"O efeito na inflação chega cheio em {months_to_peak} meses: a medida "
        f"{direction} até {_points(peak)} do IPCA em 12 meses.",
    )


def measure_in_force(title: str, tickers: list[str]) -> Headline:
    return Headline(
        NewsType.MEASURE_VOTED, f"Passa a valer: {title}", None, tuple(tickers)
    )


# Vida dos partidos


def party_founded(founder: str, abbr: str, name: str) -> Headline:
    return Headline(
        NewsType.PARTY_LIFE,
        f"{founder} funda o {abbr}, {name}",
        party_abbrs=(abbr,),
    )


def donation(donor: str, abbr: str, amount: Decimal) -> Headline:
    return Headline(
        NewsType.PARTY_LIFE,
        f"{donor} doa {format_money(amount)} ao {abbr}",
        "A doação vai para a campanha do 2º turno.",
        party_abbrs=(abbr,),
    )


def expelled(member: str, abbr: str) -> Headline:
    return Headline(
        NewsType.PARTY_LIFE, f"{member} é expulso do {abbr}", party_abbrs=(abbr,)
    )


def federation_formed(first: str, second: str, candidate: str, ends: date) -> Headline:
    """A federação formada: os dois partidos vão numa chapa e numa lista só até o fim do prazo."""
    return Headline(
        NewsType.PARTY_LIFE,
        f"{first} e {second} formam federação e vão juntos até {ends.year}",
        f"{candidate} será o candidato dos dois partidos, e o voto de cada um soma na lista da Câmara.",
    )


def federation_left(leaver: str, other_abbr: str) -> Headline:
    """Quem sai antes do prazo desfaz a federação (`leaver` é o nome do partido, `other_abbr` a sigla do parceiro)."""
    return Headline(
        NewsType.PARTY_LIFE,
        f"{leaver} deixa a federação com o {other_abbr} antes do prazo",
        f"Com a saída, a federação se desfaz. {leaver} fica impedido de se federar "
        "na eleição seguinte e passa a disputar sozinho.",
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
) -> Headline:
    """O acordo de apoio fechado: o aliado entra na base e a manchete diz em que pé a base fica e, se a emenda tem endereço, para que setor ela vai."""
    position = "na maioria" if base_seats >= majority else "abaixo da maioria"
    where = f" A emenda vai para {sector}." if sector else ""
    return Headline(
        NewsType.PARTY_LIFE,
        f"{ally_abbr} entra na base do governo de {president}",
        f"São {ally_seats} cadeiras: a base vai a {base_seats}, {position} de {majority}. "
        f"O acordo vale até {end.day:02d}/{end.month:02d}/{end.year}, com emendas "
        f"pagas todo mês.{where}",
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
        party_abbrs=(ally_abbr,),
    )


def deal_left(
    president: str,
    ally_abbr: str,
    ally_seats: int,
    base_seats: int,
    majority: int,
) -> Headline:
    """A bancada deixa a base porque o governo fraco não aceitou pagar mais; não há quebra nem culpado."""
    position = "abaixo" if base_seats < majority else "ainda acima"
    return Headline(
        NewsType.PARTY_LIFE,
        f"O {ally_abbr} deixa a base do governo",
        f"Com a aprovação de {president} em baixa, a bancada não segue apoiando sem o "
        f"reajuste que cobrou. São {ally_seats} cadeiras: a base cai para {base_seats}, "
        f"{position} da maioria de {majority}.",
        party_abbrs=(ally_abbr,),
    )


def deals_ended(abbrs: list[str], new_congress: bool) -> Headline:
    cause = "com a posse do novo Congresso" if new_congress else "pelo prazo"
    return Headline(
        NewsType.PARTY_LIFE,
        f"Acabam os acordos de apoio com {_join(abbrs)}",
        f"Os acordos terminaram {cause}, e as emendas deixam de ser pagas.",
        party_abbrs=tuple(abbrs),
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
                party_abbrs=(abbr, rival_abbr),
            )
        if band is DiceBand.VIRAL:
            return Headline(
                NewsType.CAMPAIGN,
                f"Ataque do {abbr} ao {rival_abbr} viraliza {_among(group)}",
                VIRAL_DEKS[action_id % len(VIRAL_DEKS)],
                party_abbrs=(abbr, rival_abbr),
            )
        return Headline(
            NewsType.CAMPAIGN,
            f"{abbr} parte para o ataque contra o {rival_abbr} {_among(group)}",
            ATTACK_DEKS[action_id % len(ATTACK_DEKS)],
            party_abbrs=(abbr, rival_abbr),
        )
    if band is DiceBand.VIRAL:
        text = (
            f"Propaganda do {abbr} na TV viraliza"
            if kind is CampaignActionKind.TV or group is None
            else f"{ACTION_NOUN[kind]} do {abbr} {_with(group)} viraliza"
        )
        return Headline(
            NewsType.CAMPAIGN,
            text,
            VIRAL_DEKS[action_id % len(VIRAL_DEKS)],
            party_abbrs=(abbr,),
        )
    if band is DiceBand.DISASTER:
        text = (
            f"Propaganda do {abbr} na TV vira polêmica"
            if kind is CampaignActionKind.TV or group is None
            else f"Candidato do {abbr} se envolve em polêmica no "
            f"{ACTION_NOUN[kind].lower()} {_with(group)}"
        )
        return Headline(
            NewsType.CAMPAIGN,
            text,
            DISASTER_DEKS[action_id % len(DISASTER_DEKS)],
            party_abbrs=(abbr,),
        )
    return None


def promises_set(
    abbr: str, count: int, had_promises: bool, retreated: list[str] | None = None
) -> Headline:
    """`retreated` traz as promessas já anunciadas que a nova lista abandonou (retirou, trocou ou baixou)."""
    if retreated:
        dek = (
            f"Deixou de prometer: {_join(retreated)}. Voltar atrás soma rejeição "
            "entre quem queria a medida."
        )
        if count == 0:
            return Headline(
                NewsType.CAMPAIGN,
                f"{abbr} retira as promessas de campanha",
                dek,
                party_abbrs=(abbr,),
            )
        text = (
            f"{abbr} volta atrás em uma promessa de campanha"
            if len(retreated) == 1
            else f"{abbr} volta atrás em {len(retreated)} promessas de campanha"
        )
        return Headline(NewsType.CAMPAIGN, text, dek, party_abbrs=(abbr,))
    if count == 0:
        return Headline(
            NewsType.CAMPAIGN,
            f"{abbr} retira as promessas de campanha",
            party_abbrs=(abbr,),
        )
    noun = "promessa" if count == 1 else "promessas"
    verb = "revê" if had_promises else "anuncia"
    return Headline(
        NewsType.CAMPAIGN,
        f"{abbr} {verb} as promessas de campanha",
        f"São {count} {noun}, cobradas no fim do mandato se a chapa vencer.",
        party_abbrs=(abbr,),
    )


def promises_settled(abbr: str, kept: int, total: int) -> Headline:
    return Headline(
        NewsType.CAMPAIGN,
        f"Fim do mandato: o {abbr} cumpre {kept} de {total} promessas",
        "Promessa cumprida soma afinidade; descumprida soma rejeição.",
        party_abbrs=(abbr,),
    )


def endorsement(abbr: str, endorsed_abbr: str | None) -> Headline:
    if endorsed_abbr is None:
        return Headline(
            NewsType.CAMPAIGN,
            f"{abbr} fica neutro no 2º turno",
            party_abbrs=(abbr,),
        )
    return Headline(
        NewsType.CAMPAIGN,
        f"{abbr} declara apoio ao {endorsed_abbr} no 2º turno",
        party_abbrs=(abbr, endorsed_abbr),
    )
