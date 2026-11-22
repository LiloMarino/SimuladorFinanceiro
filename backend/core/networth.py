"""A definição do patrimônio do jogador, a única da partida: snapshot, carteira, crédito e ranking leem dela."""

from decimal import Decimal


def assets_value(
    *, cash: Decimal, equity: Decimal, fixed: Decimal, locked: Decimal
) -> Decimal:
    """
    O que o jogador tem, sem descontar a dívida: o caixa, as ações a preço de mercado, a
    renda fixa e o saldo das contas travadas (o FGTS), que só sai por regra da profissão.
    """
    return cash + equity + fixed + locked


def networth(
    *,
    cash: Decimal,
    equity: Decimal,
    fixed: Decimal,
    locked: Decimal,
    debt: Decimal,
) -> Decimal:
    """O patrimônio líquido: o que o jogador tem menos o que deve."""
    return assets_value(cash=cash, equity=equity, fixed=fixed, locked=locked) - debt
