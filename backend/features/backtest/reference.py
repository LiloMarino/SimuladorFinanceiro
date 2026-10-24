"""A carteira de referência do backtest: o mesmo dinheiro e os mesmos aportes, no CDI e no Ibovespa."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.enum import IndicatorSeries
from backend.core.indicators import last_known_value
from backend.features.statistics.risk import cdi_return


@dataclass(frozen=True)
class ReferencePoint:
    day: date
    # Saldo inicial mais os aportes até o dia
    contributed: Decimal
    cdi: Decimal
    ibov: Decimal | None


class ReferenceWallet:
    """
    O saldo inicial e cada aporte entram no dia em que o jogador os recebe: no CDI
    rendem a taxa do dia útil anterior, e no Ibovespa compram cotas ao fechamento do
    dia. Sem dado do índice no primeiro dia, a linha do Ibovespa não existe.

    O andamento (dia a dia) e o resultado (refeito sobre os snapshots) passam por
    aqui, e por isso as duas linhas do gráfico são a mesma conta.
    """

    def __init__(self, starting_cash: Decimal) -> None:
        self._pending_cash = starting_cash
        self._contributed = Decimal(0)
        self._cdi = Decimal(0)
        self._units = Decimal(0)
        self._ibov_available = True
        self._started = False

    def step(self, day: date, contribution: Decimal) -> ReferencePoint:
        """Avança um pregão; `contribution` é o aporte recebido nele (zero na maioria dos dias)."""
        deposit = contribution + self._pending_cash
        self._pending_cash = Decimal(0)

        self._cdi = self._cdi * (1 + cdi_return(day)) + deposit
        self._contributed += deposit

        level = last_known_value(IndicatorSeries.IBOV, day)
        if not self._started and not level:
            self._ibov_available = False
        self._started = True
        ibov: Decimal | None = None
        if self._ibov_available and level:
            self._units += deposit / level
            ibov = self._units * level
        return ReferencePoint(day, self._contributed, self._cdi, ibov)


def references_from_contributions(
    starting_cash: Decimal, totals: list[tuple[date, Decimal]]
) -> list[ReferencePoint]:
    """
    A série de referência de um backtest salvo, a partir do aporte acumulado em cada
    pregão (`total_contribution` dos snapshots, em ordem de data).
    """
    wallet = ReferenceWallet(starting_cash)
    previous = Decimal(0)
    points = []
    for day, total in totals:
        points.append(wallet.step(day, total - previous))
        previous = total
    return points
