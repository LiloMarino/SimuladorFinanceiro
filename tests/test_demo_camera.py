import pytest

from scripts.demo.camera import (
    MAX_ZOOM,
    MERGE_GAP,
    Action,
    Rect,
    group_shots,
    keyframes,
    view_at,
)

VIEWPORT = Rect(0, 0, 1600, 900)
BUTTON = Rect(1400, 820, 180, 40)


def sample(frames, start: float, end: float, step: float = 0.05):
    moment = start
    while moment <= end:
        yield moment, view_at(frames, moment)
        moment += step


def test_actions_close_in_time_share_a_shot():
    actions = [Action(1.0, BUTTON), Action(1.0 + MERGE_GAP, BUTTON)]
    assert len(group_shots(actions)) == 1


def test_actions_far_apart_get_their_own_shots():
    actions = [Action(1.0, BUTTON), Action(1.0 + MERGE_GAP + 0.1, BUTTON)]
    assert len(group_shots(actions)) == 2


def test_view_stays_inside_the_screen_with_the_screen_proportion():
    frames = keyframes([Action(2.0, BUTTON), Action(6.0, Rect(0, 0, 50, 30))], VIEWPORT)
    for _, view in sample(frames, 0, 10):
        assert view.x >= -1e-6
        assert view.y >= -1e-6
        assert view.right <= VIEWPORT.width + 1e-6
        assert view.bottom <= VIEWPORT.height + 1e-6
        assert view.width / view.height == pytest.approx(16 / 9)


def test_zoom_never_passes_the_limit():
    frames = keyframes([Action(2.0, Rect(800, 450, 4, 4))], VIEWPORT)
    for _, view in sample(frames, 0, 5):
        assert VIEWPORT.width / view.width <= MAX_ZOOM + 1e-6


def test_camera_is_zoomed_at_the_click_and_back_to_full_screen_after():
    frames = keyframes([Action(2.0, BUTTON)], VIEWPORT)
    assert view_at(frames, 0.0) == VIEWPORT
    assert view_at(frames, 2.0).width < VIEWPORT.width
    assert view_at(frames, 10.0) == VIEWPORT


def test_wide_element_gets_no_zoom():
    frames = keyframes([Action(2.0, Rect(0, 0, 1500, 800))], VIEWPORT)
    assert view_at(frames, 2.0) == VIEWPORT


def test_close_shots_pan_without_passing_through_full_screen():
    second = Rect(100, 100, 120, 40)
    frames = keyframes([Action(2.0, BUTTON), Action(4.0, second)], VIEWPORT)
    assert all(view != VIEWPORT for _, view in sample(frames, 2.0, 4.0))
