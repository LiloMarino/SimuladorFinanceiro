"""O painel do Fundo Soberano: a carteira com a fatia de cada ativo. Tudo função pura."""

from collections.abc import Callable
from decimal import ROUND_FLOOR, Decimal

from backend.core.dto.position import PositionDTO
from backend.core.dto.sovereign_fund import SovereignPositionDTO
from backend.features.sovereign_fund import rules

# O nome e o total de papéis de um ticker: nulo no total quando o número não existe
Issued = Callable[[str], tuple[str, Decimal | None, bool]]


def build_positions(
    positions: list[PositionDTO], issued: Issued
) -> list[SovereignPositionDTO]:
    """Uma linha por ativo, da maior posição para a menor; fatia e folga só existem com o número de papéis."""
    rows = []
    for position in positions:
        name, total, is_fund = issued(position.ticker)
        rows.append(
            SovereignPositionDTO(
                ticker=position.ticker,
                name=name,
                is_fund=is_fund,
                size=position.size,
                avg_price=position.avg_price,
                current_price=position.current_price,
                current_value=position.current_value,
                return_value=position.return_value,
                stake=rules.stake(position.size, total) if total else None,
                room=(
                    rules.room(position.size, total).to_integral_value(ROUND_FLOOR)
                    if total
                    else None
                ),
            )
        )
    return sorted(rows, key=lambda row: row.current_value, reverse=True)
