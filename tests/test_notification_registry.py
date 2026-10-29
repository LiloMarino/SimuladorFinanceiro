"""O registro dos tipos de notificação: completo, ordenado pela importância e com padrões coerentes."""

from backend.core.enum import NewsLevel, NewsType, ToastType
from backend.features.notifications import registry


def test_every_news_type_is_registered_once() -> None:
    assert [spec.type for spec in registry.NEWS].count(NewsType.CAMPAIGN) == 1
    assert set(registry.NEWS_BY_TYPE) == set(NewsType)


def test_every_toast_type_is_registered_once() -> None:
    assert len(registry.TOASTS) == len(ToastType)
    assert set(registry.TOASTS_BY_TYPE) == set(ToastType)


def test_news_follow_the_section_order() -> None:
    order = [s.section for s in registry.SECTIONS]
    positions = [order.index(spec.section) for spec in registry.NEWS]

    assert positions == sorted(positions)


def test_fixed_types_open_the_window() -> None:
    fixed = [spec for spec in registry.NEWS if spec.fixed]

    assert [spec.type for spec in fixed] == [NewsType.ELECTION_RESULT]
    assert all(spec.default_level is NewsLevel.WINDOW for spec in fixed)


def test_news_levels_keep_the_choice_and_fill_the_rest() -> None:
    levels = registry.news_levels({NewsType.PARTY_LIFE: NewsLevel.OFF})

    assert levels[NewsType.PARTY_LIFE] is NewsLevel.OFF
    assert levels[NewsType.TERM_STARTED] is NewsLevel.JOURNAL
    assert set(levels) == set(NewsType)


def test_news_levels_ignore_a_choice_for_a_fixed_type() -> None:
    levels = registry.news_levels({NewsType.ELECTION_RESULT: NewsLevel.OFF})

    assert levels[NewsType.ELECTION_RESULT] is NewsLevel.WINDOW


def test_toasts_on_keep_the_choice_and_fill_the_rest() -> None:
    on = registry.toasts_on({ToastType.LIFE_EVENT: False})

    assert on[ToastType.LIFE_EVENT] is False
    assert on[ToastType.ORDER_EXECUTED] is True
    assert set(on) == set(ToastType)
