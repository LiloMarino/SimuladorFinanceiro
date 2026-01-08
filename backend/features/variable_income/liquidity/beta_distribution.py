from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class PriceLevel:
    price: float
    weight: float


class BetaLiquidityDistribution:
    def __init__(
        self,
        *,
        levels: int = 30,
        tick_size: float = 0.01,
        alpha: float = 4,
        beta: float = 4,
    ):
        self.levels = levels
        self.tick_size = tick_size
        self.alpha = alpha
        self.beta = beta

    def generate(
        self,
        *,
        low: float,
        high: float,
    ) -> list[PriceLevel]:
        if high <= low:
            return []

        prices = self._price_levels(low, high)
        weights = [self._beta_pdf(p, low, high) for p in prices]

        total = sum(weights)
        if total == 0:
            return []

        return [
            PriceLevel(price=p, weight=w / total)
            for p, w in zip(prices, weights, strict=False)
        ]

    # =========================
    # Helpers
    # =========================

    def _price_levels(self, low: float, high: float) -> list[float]:
        span = high - low
        raw = [low + span * i / (self.levels - 1) for i in range(self.levels)]
        return [self._round_tick(p) for p in raw]

    def _beta_pdf(self, price: float, low: float, high: float) -> float:
        x = (price - low) / (high - low)
        if x <= 0 or x >= 1:
            return 0.0

        a, b = self.alpha, self.beta
        return (x ** (a - 1)) * ((1 - x) ** (b - 1))

    def _round_tick(self, price: float) -> float:
        return round(price / self.tick_size) * self.tick_size
