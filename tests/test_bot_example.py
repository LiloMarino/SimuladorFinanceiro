from pathlib import Path
from types import ModuleType

EXAMPLE = (
    Path(__file__).parents[1]
    / "docs"
    / "static"
    / "exemplos"
    / "bot_cruzamento_medias.py"
)


def load_example() -> ModuleType:
    # Executa o código-fonte direto: importar gravaria __pycache__ ao lado do exemplo publicado
    module = ModuleType("bot_cruzamento_medias")
    code = compile(EXAMPLE.read_text(encoding="utf-8"), str(EXAMPLE), "exec")
    exec(code, module.__dict__)
    return module


decide = load_example().decide


def test_buys_when_short_average_crosses_above_long():
    # Queda longa e subida brusca no último dia: a curta passa a longa hoje
    closes = [10.0] * 8 + [9.0, 8.0, 7.0, 6.0, 5.0, 20.0]
    assert decide(closes, 2, 6) == "buy"


def test_sells_when_short_average_crosses_below_long():
    closes = [10.0] * 8 + [11.0, 12.0, 13.0, 14.0, 15.0, 1.0]
    assert decide(closes, 2, 6) == "sell"


def test_no_signal_while_short_stays_on_the_same_side():
    closes = [float(n) for n in range(1, 20)]
    assert decide(closes, 2, 6) is None


def test_no_signal_without_enough_history():
    assert decide([1.0, 2.0, 3.0], 2, 6) is None
    # Precisa de long + 1 fechamentos: a média longa de hoje e a de ontem
    assert decide([1.0] * 6, 2, 6) is None


def test_guide_embeds_the_example_verbatim():
    guide = EXAMPLE.parents[2] / "docs" / "como-usar" / "bot-pela-api.md"
    source = EXAMPLE.read_text(encoding="utf-8").rstrip("\n")
    assert f"```python\n{source}\n```" in guide.read_text(encoding="utf-8")
