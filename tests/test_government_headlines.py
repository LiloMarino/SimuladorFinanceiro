from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import (
    CampaignActionKind,
    DiceBand,
    MeasureKind,
    NewsType,
    VoterGroup,
)
from backend.features.government import headlines


def test_the_closed_tickets_name_who_runs_without_a_vice():
    closed = headlines.tickets_closed(
        [("AAA", "Alice", "Bob"), ("NOVO", "Dr. Paulo", None)], 63
    )

    assert closed.text == "Chapas fechadas: Alice e Bob pelo AAA e Dr. Paulo pelo NOVO"
    assert closed.dek == "O NOVO concorre sem vice. Faltam 63 dias para o 1º turno."


def test_the_round_result_carries_the_share_of_the_valid_votes():
    won = headlines.round_won(1, "Alice", "AAA", Decimal("0.5234"))
    runoff = headlines.runoff_called(
        [("AAA", Decimal("0.41")), ("NOVO", Decimal("0.33"))], date(2021, 10, 31)
    )

    assert (
        won.text
        == "Alice (AAA) vence a eleição no 1º turno, com 52,3% dos votos válidos"
    )
    assert won.news_type is NewsType.ELECTION_RESULT
    assert runoff.text == "AAA e NOVO vão ao 2º turno"
    assert runoff.dek is not None and runoff.dek.endswith("A votação é em 31/10.")


@pytest.mark.parametrize(
    ("kind", "band", "group", "rival", "expected"),
    [
        (CampaignActionKind.RALLY, DiceBand.GOOD, VoterGroup.RETIREES, None, None),
        (
            CampaignActionKind.RALLY,
            DiceBand.VIRAL,
            VoterGroup.RETIREES,
            None,
            "Comício do AAA com os aposentados viraliza",
        ),
        (
            CampaignActionKind.TV,
            DiceBand.DISASTER,
            None,
            None,
            "Propaganda do AAA na TV vira polêmica",
        ),
        (
            CampaignActionKind.ATTACK,
            DiceBand.GOOD,
            VoterGroup.WELFARE,
            "NOVO",
            "AAA parte para o ataque contra o NOVO entre quem depende de auxílio",
        ),
        (
            CampaignActionKind.ATTACK,
            DiceBand.DISASTER,
            VoterGroup.INVESTORS,
            "NOVO",
            "Ataque do AAA ao NOVO sai pela culatra entre os investidores",
        ),
    ],
)
def test_the_journal_gets_the_action_that_stands_out_and_every_attack(
    kind, band, group, rival, expected
):
    headline = headlines.campaign_action(7, kind, band, "AAA", group, rival)

    assert (headline.text if headline else None) == expected


def test_the_promises_headline_follows_the_list():
    assert headlines.promises_set("AAA", 0, True).text == (
        "AAA retira as promessas de campanha"
    )
    revised = headlines.promises_set("AAA", 1, True)
    assert revised.text == "AAA revê as promessas de campanha"
    assert revised.dek is not None and revised.dek.startswith("São 1 promessa,")


def test_impeachment_without_a_vice_names_the_computer_party_that_takes_office():
    ousted = headlines.impeachment("Bia", "FDS", None, 70, 31, "UPR")

    assert (
        ousted.text
        == "Casa tira Bia (FDS) da Presidência por 70 a 31; UPR assume o governo"
    )
    assert ousted.dek is not None and "(UPR)" in ousted.dek


def test_the_turnaround_names_who_led_the_first_round_and_lost():
    turned = headlines.round_won(2, "Bia", "FDS", Decimal("0.52"), "AAA")

    assert (
        turned.text == "Virada: Bia (FDS) vence o 2º turno, com 52% dos votos válidos"
    )
    assert turned.dek is not None and turned.dek.startswith("O AAA tinha liderado")
    assert headlines.round_won(2, "Bia", "FDS", Decimal("0.52")).text.startswith("Bia")


def test_the_house_taking_office_names_the_biggest_bloc_and_the_government_bench():
    seated = headlines.house_seated(("MRC", 38), 101, ("AAA", 21), 51)
    neutral = headlines.house_seated(("MRC", 38), 101, None, 51)

    assert seated.news_type is NewsType.TERM_STARTED
    assert (
        seated.text
        == "Novo Congresso toma posse: MRC é a maior bancada, com 38 das 101 cadeiras"
    )
    assert (
        seated.dek
        == "A bancada do governo (AAA) começa com 21 cadeiras, abaixo da maioria de 51."
    )
    assert neutral.dek is None


def test_a_deal_made_tells_where_the_base_stands():
    made = headlines.deal_made("Alice", "UPR", 16, 40, 51, date(2025, 12, 31))

    assert made.news_type is NewsType.PARTY_LIFE
    assert made.text == "UPR entra na base do governo de Alice"
    assert made.dek is not None
    assert "a base vai a 40, abaixo da maioria de 51" in made.dek
    assert "até 31/12/2025" in made.dek


def test_a_spending_vote_says_whether_spending_rises_and_what_inflation_does():
    approved = headlines.spending_voted(
        MeasureKind.WELFARE_SPENDING,
        "Auxílio: 2% do PIB",
        True,
        date(2022, 2, 1),
        Decimal("0.5"),
        6,
        60,
        41,
        2,
    )
    cut = headlines.spending_voted(
        MeasureKind.PUBLIC_WORKS,
        "Obras: 1% do PIB",
        True,
        None,
        Decimal("-0.15"),
        6,
        55,
        46,
        0,
    )
    barred = headlines.spending_voted(
        MeasureKind.SERVANT_RAISE,
        "Servidores: reajuste de 1% acima da inflação",
        False,
        None,
        Decimal("0.2"),
        6,
        40,
        61,
        0,
    )

    assert (
        approved.text
        == "Casa aprova mais gasto com auxílio por 60 a 41: Auxílio: 2% do PIB"
    )
    assert approved.dek is not None
    assert "Vale a partir de 01/02/2022." in approved.dek
    assert approved.dek.endswith("O IPCA deve subir até 0,5 ponto em 6 meses.")
    assert cut.text.startswith("Casa aprova corte em obras por 55 a 46")
    assert cut.dek is not None and cut.dek.endswith(
        "O IPCA deve ceder até 0,15 ponto em 6 meses."
    )
    assert barred.text.startswith("Casa barra mais gasto com servidores por 61 a 40")
    assert barred.dek == "Placar 40 a 61. Nada muda."


def test_a_spending_measure_in_force_tells_when_the_inflation_effect_peaks():
    in_force = headlines.spending_in_force("Auxílio: 2% do PIB", Decimal("0.5"), 6)

    assert in_force.text == "Passa a valer: Auxílio: 2% do PIB"
    assert in_force.dek is not None
    assert "cheio em 6 meses" in in_force.dek
    assert "soma até 0,5 ponto do IPCA" in in_force.dek


def test_going_back_on_a_promise_names_what_was_given_up():
    one = headlines.promises_set(
        "AAA", 1, True, ["Ações: IR das vendas com lucro em 10%"]
    )
    none = headlines.promises_set("AAA", 0, True, ["Obras: 1% do PIB"])
    two = headlines.promises_set("AAA", 1, True, ["A", "B"])

    assert one.text == "AAA volta atrás em uma promessa de campanha"
    assert one.dek is not None and one.dek.startswith("Deixou de prometer: Ações: IR")
    assert none.text == "AAA retira as promessas de campanha"
    assert none.dek is not None and "Obras: 1% do PIB" in none.dek
    assert two.text == "AAA volta atrás em 2 promessas de campanha"
