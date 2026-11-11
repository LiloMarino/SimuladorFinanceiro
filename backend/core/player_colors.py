"""
Paleta de cores dos jogadores.

As chaves são `chart-N`: o servidor decide quem tem qual cor e o front traduz a chave
para a cor (`--player-N`). O tamanho da paleta é o teto de jogadores.
"""

PLAYER_COLORS: tuple[str, ...] = tuple(f"chart-{n}" for n in range(1, 13))

MAX_PLAYERS = len(PLAYER_COLORS)


def first_free_color(taken: set[str]) -> str:
    """Primeira cor da paleta que não está em `taken`."""
    for color in PLAYER_COLORS:
        if color not in taken:
            return color
    raise ValueError("Todas as cores da paleta já têm dono.")
