import backtrader as bt

from strategies.minha_estrategia import MinhaEstrategia
from utils.data_loader import StockData, get_stock_data

# Criando o motor de simulação (Cerebro)
cerebro = bt.Cerebro()

# Configuração de capital inicial
cerebro.broker.set_cash(10000.0)

# Carregar os dados de PETR4
df = get_stock_data("PETR4.SA")
data_feed = StockData(dataname=df)

# Adicionar os dados e estratégia ao Backtrader
cerebro.adddata(data_feed)
cerebro.addstrategy(MinhaEstrategia)

# Executar a simulação
print("Executando a simulação...")
cerebro.run()

# Mostrar resultado final
print(f"Capital final: R${cerebro.broker.getvalue():.2f}")

# Opcional: Plotar os resultados
cerebro.plot()
