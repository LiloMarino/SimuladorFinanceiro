import backtrader as bt


class MinhaEstrategia(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(period=20)

    def next(self):
        if (
            self.data.close[0] > self.sma[0]
        ):  # Compra se preço fechar acima da média móvel
            self.buy()
        elif self.data.close[0] < self.sma[0]:  # Vende se preço fechar abaixo
            self.sell()
