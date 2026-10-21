"""
Dos quadros gravados aos arquivos: um MP4 por cena com o zoom da câmera, o tour inteiro
num MP4 só e um GIF curto por cena para o README, que no GitHub só anima GIF.
"""

import bisect
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from backend.core.utils import PROJECT_ROOT
from scripts.demo.camera import keyframes, view_at
from scripts.demo.director import VIEWPORT, Frame, Scene

OUTPUT_SIZE = (1920, 1080)
FPS = 30
# Qualidade do H.264: quanto menor, mais nítido e maior; 23 é o padrão do encoder
CRF = 23
# O GitHub não mostra imagens acima de 10 MB no README
GIF_MAX_BYTES = 10 * 1024 * 1024
# Do mais nítido ao mais leve: a primeira tentativa que couber vale
GIF_ATTEMPTS = ((800, 10, 80), (640, 8, 70))
GIFSKI = PROJECT_ROOT / "node_modules" / "gifski" / "bin" / "windows" / "gifski.exe"


def ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path is None:
        raise RuntimeError("ffmpeg não encontrado no PATH.")
    return path


def gifski() -> str:
    if GIFSKI.exists():
        return str(GIFSKI)
    path = shutil.which("gifski")
    if path is None:
        raise RuntimeError("gifski não encontrado: rode `pnpm install` na raiz.")
    return path


def render_scene(frames: list[Frame], scene: Scene, output: Path) -> None:
    """
    Cada quadro de saída mostra o último quadro gravado até aquele instante, recortado
    onde a câmera está. O recorte em ponto flutuante é o que deixa o zoom sem tremer.
    """
    times = [frame.time for frame in frames]
    camera = keyframes(scene.actions, VIEWPORT)
    total = int((scene.end - scene.start) * FPS)
    encoder = subprocess.Popen(
        [
            ffmpeg(), "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{OUTPUT_SIZE[0]}x{OUTPUT_SIZE[1]}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF),
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(output),
        ],
        stdin=subprocess.PIPE,
    )  # fmt: skip
    assert encoder.stdin is not None
    source_index, source, last_key, last_output = -1, None, None, b""
    for index in range(total):
        moment = scene.start + index / FPS
        frame_index = max(bisect.bisect_right(times, moment) - 1, 0)
        view = view_at(camera, moment)
        key = (frame_index, view)
        if key != last_key:
            if frame_index != source_index:
                source = Image.open(frames[frame_index].path).convert("RGB")
                source_index = frame_index
            assert source is not None
            scale = source.width / VIEWPORT.width
            box = (
                view.x * scale,
                view.y * scale,
                view.right * scale,
                view.bottom * scale,
            )
            last_output = source.resize(
                OUTPUT_SIZE, Image.Resampling.LANCZOS, box=box
            ).tobytes()
            last_key = key
        encoder.stdin.write(last_output)
    encoder.stdin.close()
    if encoder.wait() != 0:
        raise RuntimeError(f"O ffmpeg falhou ao gerar {output}.")


def concat(clips: list[Path], output: Path) -> None:
    """Junta os MP4s sem recodificar: todos saem do mesmo encoder com os mesmos parâmetros."""
    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "clips.txt"
        listing.write_text(
            "".join(f"file '{clip.resolve().as_posix()}'\n" for clip in clips),
            encoding="utf-8",
        )
        subprocess.run(
            [ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(listing), "-c", "copy", "-movflags", "+faststart", str(output)],
            check=True,
        )  # fmt: skip


def make_gif(clip: Path, output: Path) -> None:
    """O ffmpeg extrai os quadros e o gifski monta o GIF, que pela paleta por quadro fica bem mais nítido."""
    for width, fps, quality in GIF_ATTEMPTS:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [ffmpeg(), "-loglevel", "error", "-i", str(clip),
                 "-vf", f"fps={fps},scale={width}:-1:flags=lanczos",
                 str(Path(tmp) / "%05d.png")],
                check=True,
            )  # fmt: skip
            pngs = sorted(str(p) for p in Path(tmp).glob("*.png"))
            subprocess.run(
                [gifski(), "--quiet", "--fps", str(fps), "--width", str(width),
                 "--quality", str(quality), "-o", str(output), *pngs],
                check=True,
            )  # fmt: skip
        if output.stat().st_size <= GIF_MAX_BYTES:
            return
    print(f"Aviso: {output.name} passou de 10 MB mesmo na versão mais leve.")
