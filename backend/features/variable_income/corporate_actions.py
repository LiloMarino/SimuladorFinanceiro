"""O que os eventos corporativos do dia fizeram na carteira de um jogador."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class DividendReceived:
    ticker: str
    per_share: Decimal
    quantity: Decimal
    amount: Decimal


@dataclass(frozen=True)
class SplitApplied:
    ticker: str
    ratio: Decimal
    size_before: Decimal
    size_after: Decimal
    avg_price_before: Decimal
    avg_price_after: Decimal
    # Fração que sobrou numa classe de quantidade inteira e foi vendida ao close do dia
    fraction_sold: Decimal = Decimal(0)
    fraction_amount: Decimal = Decimal(0)


@dataclass
class PlayerCorporateActions:
    dividends: list[DividendReceived] = field(default_factory=list)
    splits: list[SplitApplied] = field(default_factory=list)
