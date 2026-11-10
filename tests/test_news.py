"""O jornal da partida: cada manchete fica no histórico e chega à sala inteira."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import repository
from backend.core.dependencies.simulation import get_active_simulation
from backend.core.enum import NewsType
from backend.features.notifications import news
from backend.features.notifications.news import Headline
from backend.routes.news import news_router
from tests.fakes import simulation_settings


@pytest.fixture(autouse=True)
def silent_room(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(news, "notify", lambda *_args, **_kwargs: None)


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

    history = repository.news.of_month(simulation_id, date(2020, 1, 15))
    assert [n.headline for n in history] == [
        "Congresso aprova: IR das empresas em 20%",
        "Alice funda o AAA, Partido AAA",
    ]
    assert history[0].tickers == ["PETR4", "VALE3"]
    assert history[1].dek is None
    assert [event for event, _ in sent] == ["news_published", "news_published"]
    assert sent[1][1]["news_type"] == "MEASURE_VOTED"


def test_a_headline_keeps_the_parties_it_cites(
    simulation_id: int, monkeypatch: pytest.MonkeyPatch
):
    sent: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(
        news, "notify", lambda event, payload, **_: sent.append((event, payload))
    )

    news.publish(
        simulation_id,
        date(2020, 1, 2),
        Headline(NewsType.CAMPAIGN, "AAA ataca o NOVO", party_abbrs=("AAA", "NOVO")),
    )
    news.publish(simulation_id, date(2020, 1, 2), Headline(NewsType.PARTY_LIFE, "X"))

    history = repository.news.of_month(simulation_id, date(2020, 1, 15))
    assert {n.headline: n.party_abbrs for n in history} == {
        "AAA ataca o NOVO": ["AAA", "NOVO"],
        "X": [],
    }
    assert sent[0][1]["party_abbrs"] == ["AAA", "NOVO"]


def test_a_headline_keeps_the_change_of_the_day(simulation_id: int):
    news.publish(
        simulation_id,
        date(2020, 1, 2),
        Headline(NewsType.STRONG_MOVE, "PETR4 recua 5,2%", None, ("PETR4",), -5.2),
    )
    news.publish(
        simulation_id, date(2020, 1, 2), Headline(NewsType.PARTY_LIFE, "Novo partido")
    )

    party, move = repository.news.of_month(simulation_id, date(2020, 1, 1))
    assert move.change_pct == -5.2
    assert party.change_pct is None


def test_a_month_holds_only_its_own_headlines(simulation_id: int):
    for day in (
        date(2019, 12, 31),
        date(2020, 1, 1),
        date(2020, 1, 31),
        date(2020, 2, 1),
    ):
        news.publish(
            simulation_id, day, Headline(NewsType.PARTY_LIFE, f"Partido de {day}")
        )

    january = repository.news.of_month(simulation_id, date(2020, 1, 1))
    december = repository.news.of_month(simulation_id, date(2019, 12, 1))

    assert [n.headline for n in january] == [
        "Partido de 2020-01-31",
        "Partido de 2020-01-01",
    ]
    assert [n.headline for n in december] == ["Partido de 2019-12-31"]
    assert repository.news.of_month(simulation_id, date(2020, 3, 1)) == []


def test_the_news_route_answers_one_month_and_rejects_a_bad_month(simulation_id: int):
    news.publish(
        simulation_id, date(2020, 1, 2), Headline(NewsType.PARTY_LIFE, "Janeiro")
    )
    news.publish(
        simulation_id, date(2020, 2, 3), Headline(NewsType.PARTY_LIFE, "Fevereiro")
    )
    app = FastAPI()
    app.include_router(news_router)
    app.dependency_overrides[get_active_simulation] = lambda: SimpleNamespace(
        settings=SimpleNamespace(id=simulation_id)
    )
    http = TestClient(app)

    answer = http.get("/api/news", params={"month": "2020-02"})

    assert answer.status_code == 200
    assert [n["headline"] for n in answer.json()] == ["Fevereiro"]
    assert http.get("/api/news", params={"month": "2020-13"}).status_code == 422
    assert http.get("/api/news").status_code == 422
