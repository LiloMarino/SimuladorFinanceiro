"""O noticiário: cada regra lê o retrato do pregão e devolve as manchetes, sem banco."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.core.dto.candle import CandleDTO
from backend.core.enum import AssetClass, NewsType
from backend.core.repository.economic import IndicatorHistory
from backend.features.newsroom import causes, companies, history, macro, text
from backend.features.newsroom import newsroom as newsroom_module
from backend.features.newsroom.market import MarketDay, Quote
from backend.features.newsroom.newsroom import Newsroom
from backend.features.notifications import registry
from backend.features.notifications.news import Headline


def series(rows: dict[date, str | Decimal]) -> IndicatorHistory:
    values = {day: Decimal(value) for day, value in rows.items()}
    return IndicatorHistory(dates=sorted(values), values=values)


EMPTY = series({})


def market(
    day: date = date(2020, 3, 10),
    previous: date = date(2020, 3, 9),
    quotes: list[Quote] | None = None,
    closes: dict[str, list[float]] | None = None,
    selic: IndicatorHistory = EMPTY,
    ipca: IndicatorHistory = EMPTY,
    ibov: IndicatorHistory = EMPTY,
    real_until: date | None = date(2024, 1, 1),
) -> MarketDay:
    return MarketDay(
        day=day,
        previous=previous,
        quotes=quotes or [],
        closes=closes or {},
        selic=selic,
        ipca=ipca,
        ibov=ibov,
        real_until=real_until,
        simulation_id=1,
    )


def quote(
    ticker: str = "WEGE3",
    close: float = 40.0,
    asset_class: AssetClass = AssetClass.STOCK,
    sector: str | None = "Bens Industriais",
    name: str = "WEG S.A.",
) -> Quote:
    return Quote(ticker, name, asset_class, sector, close)


# SELIC diária em % que compõe 14,75% e 14,25% ao ano em 252 dias úteis
DAILY_1475 = "0.0546124"
DAILY_1425 = "0.0528786"


def test_copom_cut_names_the_size_and_the_new_level():
    selic = series({date(2020, 3, 9): DAILY_1475, date(2020, 3, 10): DAILY_1425})

    [headline] = macro.copom_decision(market(selic=selic))

    assert headline.news_type is NewsType.COPOM_DECISION
    assert headline.text.endswith("a SELIC em 0,5 ponto, para 14,25%")
    assert headline.text.startswith(("Copom baixa", "Copom corta"))
    assert headline.dek == "A taxa básica passa de 14,75% para 14,25% ao ano."


def test_copom_hike_uses_the_rising_verbs():
    selic = series({date(2020, 3, 9): DAILY_1425, date(2020, 3, 10): DAILY_1475})

    [headline] = macro.copom_decision(market(selic=selic))

    assert headline.text.startswith(("Copom sobe", "Copom eleva"))


def test_copom_holding_the_rate_is_not_news():
    selic = series({date(2020, 3, 9): DAILY_1475, date(2020, 3, 10): DAILY_1475})

    assert macro.copom_decision(market(selic=selic)) == []


def test_the_month_inflation_comes_out_on_the_first_session_of_the_next_month():
    ipca = series(
        {date(2019, 12, 1): "0.5", date(2020, 1, 1): "0.2", date(2020, 2, 1): "0.9"}
    )

    [headline] = macro.monthly_inflation(
        market(day=date(2020, 3, 2), previous=date(2020, 2, 28), ipca=ipca)
    )

    assert headline.news_type is NewsType.MONTHLY_INFLATION
    assert headline.text in (
        "IPCA de fevereiro acelera e fica em 0,9%",
        "IPCA de fevereiro sobe para 0,9%",
    )
    assert headline.dek is not None and headline.dek.startswith(
        "Em janeiro tinha sido 0,2%."
    )


def test_the_month_inflation_waits_for_the_turn_of_the_month():
    ipca = series({date(2020, 1, 1): "0.2", date(2020, 2, 1): "0.9"})

    assert macro.monthly_inflation(market(ipca=ipca)) == []


def test_the_twelve_month_inflation_compounds_the_last_twelve_months():
    ipca = series({date(2019, month, 1): "1" for month in range(3, 13)})
    ipca = series(
        {
            **ipca.values,
            date(2020, 1, 1): Decimal(1),
            date(2020, 2, 1): Decimal(1),
        }
    )

    [headline] = macro.monthly_inflation(
        market(day=date(2020, 3, 2), previous=date(2020, 2, 28), ipca=ipca)
    )

    assert headline.dek is not None
    assert headline.dek.endswith("Em 12 meses, a inflação acumula 12,68%.")


def ibov_series(levels: list[tuple[date, str]]) -> IndicatorHistory:
    return series(dict(levels))


def test_the_ibovespa_biggest_drop_of_the_year_is_news_once():
    ibov = ibov_series(
        [
            (date(2020, 3, 5), "100000"),
            (date(2020, 3, 6), "97000"),
            (date(2020, 3, 9), "90000"),
            (date(2020, 3, 10), "88000"),
        ]
    )
    rule = macro.IbovespaExtremes()

    first = rule(market(day=date(2020, 3, 6), previous=date(2020, 3, 5), ibov=ibov))
    second = rule(market(day=date(2020, 3, 9), previous=date(2020, 3, 6), ibov=ibov))
    smaller = rule(market(day=date(2020, 3, 10), previous=date(2020, 3, 9), ibov=ibov))

    assert [h.text for h in first] == [
        "Ibovespa tem a maior queda do ano: \N{MINUS SIGN}3%"
    ]
    assert [h.text for h in second] == [
        "Ibovespa tem a maior queda do ano: \N{MINUS SIGN}7,2%"
    ]
    assert second[0].dek == "O índice fecha em 90.000 pontos."
    assert smaller == []


def test_the_ibovespa_record_does_not_repeat_on_consecutive_days():
    ibov = ibov_series(
        [
            (date(2020, 3, 5), "100000"),
            (date(2020, 3, 6), "101000"),
            (date(2020, 3, 9), "102000"),
        ]
    )
    rule = macro.IbovespaExtremes()

    first = rule(market(day=date(2020, 3, 6), previous=date(2020, 3, 5), ibov=ibov))
    second = rule(market(day=date(2020, 3, 9), previous=date(2020, 3, 6), ibov=ibov))

    assert [h.text for h in first] == ["Ibovespa fecha no recorde: 101.000 pontos"]
    assert second == []


def test_the_ibovespa_record_reads_the_past_peak_from_the_series():
    ibov = ibov_series(
        [
            (date(2020, 1, 2), "130000"),
            (date(2020, 3, 9), "100000"),
            (date(2020, 3, 10), "101000"),
        ]
    )

    assert macro.IbovespaExtremes()(market(ibov=ibov)) == []


def test_a_strong_move_carries_the_cause_for_the_sector_and_direction():
    [headline] = companies.strong_moves(
        market(quotes=[quote(close=44.0)], closes={"WEGE3": [40.0]})
    )

    assert headline.news_type is NewsType.STRONG_MOVE
    assert headline.tickers == ("WEGE3",)
    assert headline.text.startswith("WEG ") and headline.text.endswith(" 10%")
    assert headline.dek is not None
    assert headline.dek.startswith(
        "WEGE3 fecha a R$ 44,00. O mercado atribui a alta a "
    )
    cause = headline.dek.removeprefix(
        "WEGE3 fecha a R$ 44,00. O mercado atribui a alta a "
    ).removesuffix(".")
    assert cause in (*causes.UP["Bens Industriais"], *causes.GENERAL_UP)


def test_a_fall_picks_a_cause_from_the_falling_bank():
    [headline] = companies.strong_moves(
        market(quotes=[quote(close=36.0)], closes={"WEGE3": [40.0]})
    )

    assert headline.dek is not None and "atribui a queda a" in headline.dek
    assert headline.text.split()[1] in ("cai", "recua", "despenca")


def test_a_move_inside_the_limit_is_not_news():
    assert (
        companies.strong_moves(
            market(quotes=[quote(close=41.9)], closes={"WEGE3": [40.0]})
        )
        == []
    )


def test_crypto_moves_are_not_company_news():
    bitcoin = quote("BTC", 60000.0, AssetClass.CRYPTO, None, "Bitcoin")

    assert (
        companies.strong_moves(market(quotes=[bitcoin], closes={"BTC": [50000.0]}))
        == []
    )


def test_only_the_biggest_moves_of_the_day_make_the_news():
    tickers = ["AAAA3", "BBBB3", "CCCC3", "DDDD3"]
    quotes = [quote(t, 40.0 + i * 2) for i, t in enumerate(tickers)]
    closes = {t: [30.0] for t in tickers}

    headlines = companies.strong_moves(market(quotes=quotes, closes=closes))

    assert [h.tickers for h in headlines] == [("DDDD3",), ("CCCC3",), ("BBBB3",)]


def test_the_same_fact_gets_the_same_phrase_on_every_reading():
    day = market(quotes=[quote(close=44.0)], closes={"WEGE3": [40.0]})

    assert companies.strong_moves(day) == companies.strong_moves(day)


def test_a_52_week_high_needs_a_close_above_the_whole_year():
    year = [30.0 + i * 0.05 for i in range(200)]

    [headline] = companies.week_highs(
        market(quotes=[quote(close=41.0)], closes={"WEGE3": year})
    )

    assert headline.news_type is NewsType.WEEK_HIGH
    assert headline.text in (
        "WEG atinge o maior preço em um ano",
        "WEG renova a máxima de 52 semanas",
    )
    assert headline.dek == "WEGE3 fecha a R$ 41,00, 2,6% acima da máxima anterior."
    assert (
        companies.week_highs(market(quotes=[quote(close=39.0)], closes={"WEGE3": year}))
        == []
    )


def test_a_young_series_has_no_52_week_high():
    assert (
        companies.week_highs(
            market(quotes=[quote(close=41.0)], closes={"WEGE3": [30.0] * 20})
        )
        == []
    )


def test_a_milestone_comes_out_on_the_session_that_covers_its_date():
    friday_to_monday = market(
        day=date(2017, 5, 18), previous=date(2017, 5, 17), real_until=date(2024, 1, 1)
    )

    [headline] = history.historical_milestones(friday_to_monday)

    assert headline.news_type is NewsType.HISTORICAL_MILESTONE
    assert headline.text == "Joesley Day: Ibovespa cai 8,8% e o pregão para"
    assert headline.tickers == ("JBSS3",)
    assert (
        history.historical_milestones(
            market(day=date(2017, 5, 19), previous=date(2017, 5, 18))
        )
        == []
    )


def test_a_milestone_after_the_last_real_day_does_not_come_out():
    generated = market(
        day=date(2020, 3, 10), previous=date(2020, 3, 6), real_until=date(2019, 12, 31)
    )

    assert history.historical_milestones(generated) == []
    assert history.historical_milestones(market(real_until=None)) == []


def test_milestones_are_in_the_order_of_their_dates():
    days = [m.day for m in history.MILESTONES]

    assert days == sorted(days)


def test_numbers_and_names_read_in_portuguese():
    assert text.number(Decimal("14.25")) == "14,25"
    assert text.number(0.5) == "0,5"
    assert text.number(12.0) == "12"
    assert text.grouped(Decimal("134567.4")) == "134.567"
    assert text.price(1234.5) == "R$ 1.234,50"
    assert text.short_name("WEG S.A.", "WEGE3") == "WEG"
    assert text.short_name("Petróleo Brasileiro S.A. - Petrobras", "PETR4") == "PETR4"


def test_every_newsroom_type_is_in_the_registry_with_its_section():
    registered = registry.NEWS_BY_TYPE

    assert registered[NewsType.COPOM_DECISION].section.value == "ECONOMY"
    assert registered[NewsType.STRONG_MOVE].portfolio_filter
    assert registered[NewsType.WEEK_HIGH].portfolio_filter
    assert registered[NewsType.HISTORICAL_MILESTONE].section.value == "HISTORY"


def candle(ticker: str, close: float, price_date: date) -> CandleDTO:
    return CandleDTO(
        id=1,
        ticker=ticker,
        name="WEG S.A.",
        asset_class=AssetClass.STOCK,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1,
        price_date=price_date,
        change=0,
        change_pct=0,
    )


def test_the_newsroom_publishes_each_headline_with_its_day(
    monkeypatch: pytest.MonkeyPatch,
):
    published: list[tuple[date, Headline]] = []
    room = Newsroom(1, dict, lambda day, headline: published.append((day, headline)))
    room._closes = {"WEGE3": [40.0]}
    room.__dict__["_real_end"] = None
    monkeypatch.setattr(
        newsroom_module.repository,
        "economic",
        SimpleNamespace(get_history=lambda _series: EMPTY),
    )

    room.on_tick(date(2020, 3, 10), [candle("WEGE3", 44.0, date(2020, 3, 10))])

    assert [day for day, _ in published] == [date(2020, 3, 10)]
    assert published[0][1].news_type is NewsType.STRONG_MOVE


def test_the_window_keeps_only_the_closes_of_the_day_that_traded():
    room = Newsroom(1, dict, lambda *_: None)
    room._closes = {}
    stale = candle("WEGE3", 40.0, date(2020, 3, 9))

    room._append(date(2020, 3, 10), [stale])
    room._append(date(2020, 3, 10), [candle("WEGE3", 41.0, date(2020, 3, 10))])

    assert room._closes["WEGE3"] == [41.0]
