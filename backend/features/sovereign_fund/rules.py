"""As regras do Fundo Soberano: teto de fatia, favorecimento e o que cabe numa compra. Tudo função pura."""

from decimal import Decimal

ZERO = Decimal(0)

# O id da conta do fundo no cabeçalho X-Account e na lista de contas: nenhuma gestora tem o 0
ACCOUNT_ID = 0

# O fundo nunca passa de 20% das ações de uma empresa nem das cotas de uma gestora
CEILING = Decimal("0.20")

# Comprar a fatia de uma gestora aliada custa 1 ponto de rejeição a cada 6% de fatia
# ganha, em todos os grupos do eleitorado: 12% de fatia dão 2 pontos
FAVORITISM_STAKE_PER_POINT = Decimal("0.06")


# O maior aporte de uma medida só, em reais: 500 bilhões
MAX_CONTRIBUTION = Decimal(500) * Decimal(10) ** 9


def stake(held: Decimal, issued: Decimal) -> Decimal:
    """A fatia do fundo no ativo, de 0 a 1: o que ele guarda sobre o que existe em circulação."""
    return held / issued if issued > 0 else ZERO


def room(held: Decimal, issued: Decimal) -> Decimal:
    """Quanto o fundo ainda pode comprar do ativo sem passar do teto; nunca negativo."""
    return max(ZERO, issued * CEILING - held)


def favoritism_points(gained: Decimal) -> Decimal:
    """Os pontos de rejeição que a compra soma ao partido do governo, dada a fatia que o fundo ganhou na gestora."""
    return gained / FAVORITISM_STAKE_PER_POINT
