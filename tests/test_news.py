"""O jornal da partida: cada manchete fica no histórico e chega à sala inteira."""

from __future__ import annotations

from datetime import date

import pytest

from backend.core import repository
from backend.core.enum import NewsType
from backend.features.notifications import news
from backend.features.notifications.news import Headline
from tests.fakes import simulation_settings


@pytest.fixture
def simulation_id(database: object) -> int:
    return repository.simulation.create_simulation(simulation_settings())


def test_a_published_headline_stays_in_the_history_and_reaches_the_room(
    simulation_id: int, monkeypatch: pytest.MonkeyPatch
):
    sent: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(
        news, "notify", lambda event, payload, **_: sent.append((event, payload))
    )

    news.publish(
        simulation_id,
        date(2020, 1, 2),
        Headline(NewsType.PARTY_LIFE, "Alice funda o AAA, Partido AAA"),
    )
    news.publish(
        simulation_id,
        date(2020, 1, 2),
        Headline(
            NewsType.MEASURE_VOTED,
            "Congresso aprova: IR das empresas em 20%",
            "Vale a partir de 01/02/2020.",
            ("PETR4", "VALE3"),
        ),
    )

    history = repository.news.of_simulation(simulation_id)
    assert [n.headline for n in history] == [
        "Congresso aprova: IR das empresas em 20%",
        "Alice funda o AAA, Partido AAA",
    ]
    assert history[0].tickers == ["PETR4", "VALE3"]
    assert history[1].dek is None
    assert [event for event, _ in sent] == ["news_published", "news_published"]
    assert sent[1][1]["news_type"] == "MEASURE_VOTED"
