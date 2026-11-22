"""
A política do CDB da casa do Bancário-bot: aplica no CDB de 3 anos quando a SELIC de hoje
está acima da média dos últimos 24 meses, com o que o caixa tem acima da reserva e dentro
do teto. Só funções do que o bot vê, sem o motor.
"""

from decimal import Decimal

from backend.features.profession.reserve import Reserve

# A janela da média da SELIC, em meses (uma amostra por mês, a do primeiro pregão)
SELIC_AVERAGE_MONTHS = 24

# O prazo, em anos, do CDB da casa em que o bot aplica
BOT_HOUSE_CDB_YEARS = 3


def house_cdb_amount(
    selic: Decimal | None,
    average: Decimal | None,
    cap: Decimal,
    reserve: Reserve,
) -> Decimal:
    """
    O valor a aplicar no CDB da casa: o menor entre o teto e o caixa que sobra depois de um imprevisto de saúde,
    quando a SELIC anual de hoje está acima da média dos últimos `SELIC_AVERAGE_MONTHS`
    meses. Zero sem série, com a SELIC na média ou abaixo e com a reserva descoberta.
    """
    if selic is None or average is None or selic <= average:
        return Decimal(0)
    spare = reserve.cash - reserve.health_cost
    return max(min(cap, spare), Decimal(0))
