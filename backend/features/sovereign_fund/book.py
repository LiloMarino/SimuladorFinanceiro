"""O livro do Fundo Soberano: o que passou entre o fundo e o Tesouro, mês a mês."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.sovereign_fund import SovereignFlowDTO, SovereignFundDTO
from backend.core.enum import SovereignFlowKind
from backend.core.utils import last_day_of_month

ZERO = Decimal(0)


@dataclass(frozen=True)
class FundQuotas:
    """A gestora dona de uma cota: o nome, as cotas que existem e a sigla do partido do gestor."""

    name: str
    quotas: Decimal
    manager_party: str | None


# A gestora de um ticker, ou None quando o ticker não é cota de gestora
FundLookup = Callable[[str], FundQuotas | None]


def budget_month_end(day: date) -> date:
    """O fim do mês do orçamento em que o fato do dia entra: o do dia, ou o do seguinte se o dia é o último."""
    return last_day_of_month(day + timedelta(days=1))


class SovereignFundBook:
    """
    O caixa e as posições moram na carteira do fundo; aqui ficam os movimentos com o
    Tesouro. O aporte sai do Tesouro para o caixa do fundo; a venda e o dividendo fazem
    o caminho de volta no mesmo dia em que o caixa do fundo os recebe.
    """

    def __init__(
        self,
        simulation_id: int,
        fund: SovereignFundDTO,
        flows: Iterable[SovereignFlowDTO] = (),
    ) -> None:
        self._simulation_id = simulation_id
        self.portfolio_id = fund.portfolio_id
        self.client_id = fund.client_id
        self._flows = list(flows)

    def record(
        self,
        day: date,
        kind: SovereignFlowKind,
        amount: Decimal,
        measure_id: int | None = None,
    ) -> bool:
        """Grava o movimento; False quando o aporte dessa medida já estava gravado."""
        if amount <= ZERO:
            return False
        if not repository.sovereign_fund.add_flow(
            self._simulation_id, day, kind, amount, measure_id
        ):
            return False
        self._flows.append(
            SovereignFlowDTO(day=day, kind=kind, amount=amount, measure_id=measure_id)
        )
        return True

    def _total(self, kind: SovereignFlowKind, month_end: date | None = None) -> Decimal:
        return sum(
            (
                flow.amount
                for flow in self._flows
                if flow.kind is kind
                and (month_end is None or budget_month_end(flow.day) == month_end)
            ),
            ZERO,
        )

    def contributed(self) -> Decimal:
        """Tudo o que o Tesouro já aportou, em reais."""
        return self._total(SovereignFlowKind.CONTRIBUTION)

    def returned(self) -> Decimal:
        """Tudo o que voltou ao Tesouro, em reais: vendas e dividendos."""
        return self._total(SovereignFlowKind.SALE) + self._total(
            SovereignFlowKind.DIVIDEND
        )

    def assets_in(self, month_end: date) -> Decimal:
        """O que o fundo mudou nos ativos do Tesouro no mês: as vendas somam e o aporte tira, em reais."""
        return self._total(SovereignFlowKind.SALE, month_end) - self._total(
            SovereignFlowKind.CONTRIBUTION, month_end
        )

    def dividends_in(self, month_end: date) -> Decimal:
        """O que os dividendos do fundo renderam ao Tesouro no mês, em reais."""
        return self._total(SovereignFlowKind.DIVIDEND, month_end)
