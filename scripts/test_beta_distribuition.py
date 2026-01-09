from datetime import date

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.liquidity.beta_distribution import (
    BetaLiquidityDistribution,
)


def main():
    # -------------------------
    # Candle base
    # -------------------------
    base_candle = Candle(
        price_date=date.today(),
        ticker="TEST",
        open=1.00,
        high=1.20,
        low=0.80,
        close=1.02,
        volume=10_000,
    )

    # -------------------------
    # Figura + eixo
    # -------------------------
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(bottom=0.35)

    # linhas fixas
    ax.axvline(base_candle.low, linestyle="--", linewidth=1)
    ax.axvline(base_candle.high, linestyle="--", linewidth=1)
    typical_price = (base_candle.high + base_candle.low + base_candle.close) / 3
    ax.axvline(typical_price, linestyle=":", linewidth=2)

    ax.set_xlabel("Price")
    ax.set_ylabel("Volume (shares)")

    # -------------------------
    # Sliders
    # -------------------------
    ax_alpha = plt.axes((0.15, 0.25, 0.7, 0.03))
    ax_beta = plt.axes((0.15, 0.20, 0.7, 0.03))
    ax_levels = plt.axes((0.15, 0.15, 0.7, 0.03))
    ax_volume = plt.axes((0.15, 0.10, 0.7, 0.03))

    slider_alpha = Slider(ax_alpha, "alpha", 0.5, 10.0, valinit=4.0, valstep=0.1)
    slider_beta = Slider(ax_beta, "beta", 0.5, 10.0, valinit=4.0, valstep=0.1)
    slider_levels = Slider(ax_levels, "levels", 5, 80, valinit=40, valstep=1)
    slider_volume = Slider(
        ax_volume, "volume", 1_000, 50_000, valinit=10_000, valstep=500
    )

    # -------------------------
    # Render
    # -------------------------
    def render(_=None):
        ax.clear()

        candle = Candle(
            price_date=base_candle.price_date,
            ticker=base_candle.ticker,
            open=base_candle.open,
            high=base_candle.high,
            low=base_candle.low,
            close=base_candle.close,
            volume=int(slider_volume.val),
        )

        dist = BetaLiquidityDistribution(
            levels=int(slider_levels.val),
            tick_size=0.01,
            alpha=slider_alpha.val,
            beta=slider_beta.val,
        )

        levels = dist.generate(candle)

        prices = [lvl.price for lvl in levels]
        volumes = [lvl.volume for lvl in levels]

        ax.bar(prices, volumes, width=0.008)
        ax.set_xticks(prices)
        ax.set_xticklabels(
            [f"{p:.2f}" for p in prices],
            rotation=90,
            fontsize=8,
        )

        # linhas de referência
        ax.axvline(candle.low, linestyle="--", linewidth=1)
        ax.axvline(candle.high, linestyle="--", linewidth=1)
        typical_price = (candle.high + candle.low + candle.close) / 3
        ax.axvline(typical_price, linestyle=":", linewidth=2)

        ax.set_title(
            "Beta Liquidity Distribution (OHLCV → OrderBook)\n"
            f"alpha={slider_alpha.val:.2f}, "
            f"beta={slider_beta.val:.2f}, "
            f"levels={int(slider_levels.val)}, "
            f"volume={int(slider_volume.val)}"
        )

        ax.set_xlabel("Price")
        ax.set_ylabel("Volume (shares)")

        fig.canvas.draw_idle()

    # liga sliders
    slider_alpha.on_changed(render)
    slider_beta.on_changed(render)
    slider_levels.on_changed(render)
    slider_volume.on_changed(render)

    # primeira renderização
    render()

    plt.show()


if __name__ == "__main__":
    main()
