"""O capital político de um partido, como o painel do governo e o relatório da partida o mostram."""

from backend.core.dto.base import BaseDTO


class PoliticalCapitalDTO(BaseDTO):
    """Pontos acumulados por mês de poder; o partido com mais pontos vence a partida política."""

    total: int
    # 1 ponto por cadeira, a cada fechamento de mês
    seats: int
    # A aprovação do governo (0 a 100) a cada fechamento de mês do partido no poder
    presidency: int
    # Pontos pelas promessas cumpridas no balanço do mandato
    promises: int
    # Pontos perdidos num impeachment; nunca é positivo
    impeachment: int
