from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import CampaignActionKind, DiceBand, NewsType, VoterGroup
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
