from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.liquidity.liquidity_distribution import (
    LiquidityDistribution,
    PriceLevel,
)


class BetaLiquidityDistribution(LiquidityDistribution):
    """
    Gerador de distribuição de liquidez sintética usando Beta Distribution.

    Responsável por:
    - Calcular densidade centrípeta de ordens usando distribuição Beta
    - Dividir volume do candle entre níveis de preço de forma realista
    - Gerar price levels separados para zona de compra e venda
    - Aplicar tick_size para arredondamento de preços
    """

    def __init__(
        self,
        *,
        levels: int = 30,
        tick_size: float = 0.01,
        alpha: float = 4.0,
        beta: float = 4.0,
    ):
        if levels < 2:
            raise ValueError("levels must be >= 2")

        self.levels = levels
        self.tick_size = tick_size
        self.alpha = alpha
        self.beta = beta

    # =========================
    # Public API
    # =========================

    def generate(self, candle: Candle) -> list[PriceLevel]:
        if candle.high <= candle.low or candle.volume <= 0:
            return []

        prices = self._price_levels(candle.low, candle.high)
        pdf = [self._beta_pdf(p, candle.low, candle.high) for p in prices]

        total_density = sum(pdf)
        if total_density == 0:
            return []

        # Converte densidade em volume absoluto
        raw_volumes = [candle.volume * d / total_density for d in pdf]

        # Arredondamento conservador
        volumes = [int(v) for v in raw_volumes]

        # Ajuste de erro de arredondamento
        delta = candle.volume - sum(volumes)
        if delta != 0:
            volumes[self._center_index()] += delta

        levels: list[PriceLevel] = []
        for price, volume in zip(prices, volumes, strict=False):
            if volume <= 0:
                continue
            levels.append(
                PriceLevel(
                    price=price,
                    volume=volume,
                )
            )

        return levels

    # =========================
    # Helpers técnicos
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

    def _center_index(self) -> int:
        """
        Índice central da distribuição (usado para correção de rounding).
        """
        return self.levels // 2
