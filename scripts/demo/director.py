"""
O que o roteiro usa para gravar: mouse que desliza até o alvo, digitação com ritmo,
screenshots e cenas, com cada ação anotada para a câmera (`camera.py`).

A gravação é o screencast do DevTools: cada quadro chega em JPEG com o instante em que
foi pintado, no mesmo relógio (`time.time()`) em que as ações são anotadas.
"""

import base64
import math
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import CDPSession, Locator, Page

from scripts.demo.camera import Action, Rect

VIEWPORT = Rect(0, 0, 1600, 900)
DEVICE_SCALE = 2
JPEG_QUALITY = 90
# Velocidade do cursor, em pixels CSS por segundo, e os limites de cada deslize
CURSOR_SPEED = 1400
GLIDE_MIN, GLIDE_MAX = 0.35, 0.9
GLIDE_STEP_MS = 16
TYPING_DELAY_MS = 70


@dataclass(frozen=True)
class Frame:
    time: float
    path: Path


@dataclass
class Scene:
    name: str
    start: float
    end: float = 0.0
    actions: list[Action] = field(default_factory=list)


class Director:
    """
    Os quadros só chegam enquanto o Playwright processa eventos: as esperas passam por
    `page.wait_for_timeout`, que mantém o screencast correndo.
    """

    def __init__(self, page: Page, cdp: CDPSession, frames_dir: Path, shots_dir: Path):
        self.page = page
        self.cdp = cdp
        self.frames_dir = frames_dir
        self.shots_dir = shots_dir
        self.frames: list[Frame] = []
        self.scenes: list[Scene] = []
        self._scene: Scene | None = None
        self._mouse = (VIEWPORT.width / 2, VIEWPORT.height / 2)
        self._recording = False

    # ------------------------------------------------------------------
    # Screencast
    # ------------------------------------------------------------------

    def start_recording(self) -> None:
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self._recording = True
        self.cdp.on("Page.screencastFrame", self._on_frame)
        self.cdp.send(
            "Page.startScreencast",
            {
                "format": "jpeg",
                "quality": JPEG_QUALITY,
                "maxWidth": int(VIEWPORT.width * DEVICE_SCALE),
                "maxHeight": int(VIEWPORT.height * DEVICE_SCALE),
                "everyNthFrame": 1,
            },
        )

    def stop_recording(self) -> None:
        self._recording = False
        self.cdp.send("Page.stopScreencast")

    def _on_frame(self, event: dict) -> None:
        if not self._recording:
            return
        path = self.frames_dir / f"{len(self.frames):06d}.jpg"
        path.write_bytes(base64.b64decode(event["data"]))
        self.frames.append(Frame(event["metadata"]["timestamp"], path))
        self.cdp.send("Page.screencastFrameAck", {"sessionId": event["sessionId"]})

    # ------------------------------------------------------------------
    # Cenas e ações
    # ------------------------------------------------------------------

    @contextmanager
    def scene(self, name: str) -> Iterator[Scene]:
        """Um trecho do vídeo, que vira um MP4 e um GIF; começa e termina parado."""
        self.wait(0.6)
        scene = Scene(name, time.time())
        self._scene = scene
        try:
            yield scene
        finally:
            self.wait(1.4)
            scene.end = time.time()
            self.scenes.append(scene)
            self._scene = None

    def wait(self, seconds: float) -> None:
        self.page.wait_for_timeout(seconds * 1000)

    def click(self, target: Locator, zoom: bool = True) -> None:
        box = self._reach(target)
        self.page.mouse.down()
        self.page.mouse.up()
        if self._scene is not None and zoom:
            self._scene.actions.append(Action(time.time(), box))
        self.wait(0.3)

    def fill(self, target: Locator, text: str, zoom: bool = True) -> None:
        self.click(target, zoom)
        target.press_sequentially(text, delay=TYPING_DELAY_MS)
        if self._scene is not None and zoom:
            # A digitação estende o plano do clique até a última tecla
            self._scene.actions.append(Action(time.time(), self._box(target)))

    def hover(self, target: Locator) -> None:
        self._reach(target)

    def shot(self, name: str, target: Locator | None = None) -> Path:
        """Screenshot em pixels CSS, sem o cursor desenhado; com `target`, só dele."""
        self.shots_dir.mkdir(parents=True, exist_ok=True)
        path = self.shots_dir / f"{name}.png"
        cursor = self.page.locator("#demo-cursor")
        cursor.evaluate("el => (el.hidden = true)")
        (target or self.page).screenshot(path=path, scale="css", animations="disabled")
        cursor.evaluate("el => (el.hidden = false)")
        return path

    def _box(self, target: Locator) -> Rect:
        box = target.bounding_box()
        if box is None:
            raise RuntimeError(f"Elemento sem caixa na tela: {target}")
        return Rect(box["x"], box["y"], box["width"], box["height"])

    def _reach(self, target: Locator) -> Rect:
        """Leva o cursor ao centro do alvo, acelerando e freando como uma mão."""
        target.wait_for(state="visible")
        target.scroll_into_view_if_needed()
        box = self._box(target)
        goal = (box.x + box.width / 2, box.y + box.height / 2)
        start = self._mouse
        distance = math.dist(start, goal)
        duration = min(max(distance / CURSOR_SPEED, GLIDE_MIN), GLIDE_MAX)
        steps = max(int(duration * 1000 / GLIDE_STEP_MS), 1)
        for step in range(1, steps + 1):
            progress = _ease_out(step / steps)
            self.page.mouse.move(
                start[0] + (goal[0] - start[0]) * progress,
                start[1] + (goal[1] - start[1]) * progress,
            )
            self.page.wait_for_timeout(GLIDE_STEP_MS)
        self._mouse = goal
        return box


def _ease_out(progress: float) -> float:
    return 1 - (1 - progress) ** 3
