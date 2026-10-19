"""
Equipes do modo em equipes.

A equipe é um índice de 1 a 10 que identifica a cor dela: o servidor decide quem está
em qual equipe e o front traduz o índice para a cor (`--team-N`). O tamanho da paleta
é o teto de equipes: no limite, cada jogador está sozinho na sua.
"""

from backend.core.enum import TeamNaming

TEAM_COLOR_NAMES: tuple[str, ...] = (
    "Índigo",
    "Carmim",
    "Floresta",
    "Ouro",
    "Petróleo",
    "Ameixa",
    "Grafite",
    "Oliva",
    "Ferrugem",
    "Marinho",
)

TEAM_COUNT = len(TEAM_COLOR_NAMES)

MIN_TEAMS = 2


def is_valid_team(team: int) -> bool:
    return 1 <= team <= TEAM_COUNT


def team_name(team: int, naming: TeamNaming) -> str:
    """Nome de exibição da equipe: pela cor (padrão) ou pelo número."""
    if naming is TeamNaming.NUMBER:
        return f"Equipe {team}"
    return f"Equipe {TEAM_COLOR_NAMES[team - 1]}"
