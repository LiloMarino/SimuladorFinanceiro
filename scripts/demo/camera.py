"""
Zoom automático: das ações do roteiro ao retângulo da tela que cada quadro mostra.

Como a câmera roda depois da gravação, ela sabe de antemão onde e quando cada clique
acontece: aproxima antes, segura enquanto as ações seguem perto umas das outras e
afasta quando elas param. Tudo em pixels CSS da viewport e em segundos do relógio da
gravação.
"""

import itertools
from dataclasses import dataclass

MAX_ZOOM = 1.8
# Abaixo disso o zoom quase não se nota e só balança a tela
MIN_ZOOM = 1.15
# Folga em volta do que foi clicado, para o contexto continuar aparecendo
PADDING = 160
# Ações com até este intervalo entre si ficam no mesmo plano
MERGE_GAP = 1.5
ZOOM_IN = 0.8
# A aproximação termina um pouco antes do clique, com o cursor chegando
ZOOM_IN_LEAD = 0.1
HOLD = 1.0
ZOOM_OUT = 0.8


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def union(self, other: "Rect") -> "Rect":
        x, y = min(self.x, other.x), min(self.y, other.y)
        return Rect(
            x, y, max(self.right, other.right) - x, max(self.bottom, other.bottom) - y
        )


@dataclass(frozen=True)
class Action:
    time: float
    box: Rect


@dataclass(frozen=True)
class Keyframe:
    time: float
    view: Rect


def group_shots(actions: list[Action]) -> list[list[Action]]:
    """Ações em sequência, com intervalos de até `MERGE_GAP`, formam um plano."""
    shots: list[list[Action]] = []
    for action in sorted(actions, key=lambda a: a.time):
        if shots and action.time - shots[-1][-1].time <= MERGE_GAP:
            shots[-1].append(action)
        else:
            shots.append([action])
    return shots


def framing(box: Rect, viewport: Rect) -> Rect | None:
    """O retângulo, na proporção da tela e dentro dela, que mostra `box` com folga."""
    zoom = min(
        viewport.width / (box.width + 2 * PADDING),
        viewport.height / (box.height + 2 * PADDING),
        MAX_ZOOM,
    )
    if zoom < MIN_ZOOM:
        return None
    width, height = viewport.width / zoom, viewport.height / zoom
    center_x, center_y = box.x + box.width / 2, box.y + box.height / 2
    x = min(max(center_x - width / 2, 0), viewport.width - width)
    y = min(max(center_y - height / 2, 0), viewport.height - height)
    return Rect(x, y, width, height)


def keyframes(actions: list[Action], viewport: Rect) -> list[Keyframe]:
    """
    Os pontos em que a câmera para numa posição. Entre um e outro ela se move com
    easing; quando o próximo plano começa antes de o anterior terminar de afastar, a
    câmera vai direto de um enquadramento ao outro, sem voltar à tela inteira.
    """
    frames = [Keyframe(float("-inf"), viewport)]
    for shot in group_shots(actions):
        box = shot[0].box
        for action in shot[1:]:
            box = box.union(action.box)
        view = framing(box, viewport)
        if view is None:
            continue
        arrive = shot[0].time - ZOOM_IN_LEAD
        depart = shot[-1].time + HOLD
        start = arrive - ZOOM_IN
        if len(frames) > 1 and frames[-1].time > start:
            # O afastamento do plano anterior dá lugar ao movimento até este
            frames.pop()
            start = max(frames[-1].time, start)
        frames.append(Keyframe(start, frames[-1].view))
        frames.append(Keyframe(arrive, view))
        frames.append(Keyframe(depart, view))
        frames.append(Keyframe(depart + ZOOM_OUT, viewport))
    return frames


def ease_in_out(progress: float) -> float:
    if progress < 0.5:
        return 4 * progress**3
    return 1 - (-2 * progress + 2) ** 3 / 2


def view_at(frames: list[Keyframe], time: float) -> Rect:
    """Onde a câmera está no instante `time`."""
    for before, after in itertools.pairwise(frames):
        if before.time <= time < after.time:
            if before.view == after.view:
                return before.view
            progress = ease_in_out((time - before.time) / (after.time - before.time))
            a, b = before.view, after.view
            return Rect(
                a.x + (b.x - a.x) * progress,
                a.y + (b.y - a.y) * progress,
                a.width + (b.width - a.width) * progress,
                a.height + (b.height - a.height) * progress,
            )
    return frames[-1].view if time >= frames[-1].time else frames[0].view
