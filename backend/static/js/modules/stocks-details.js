const container = document.getElementById("stock-graph");
const stockHistory = window.initialStockData || [];
const ticker = window.stockTicker || "UNKNOWN";

// Inicializa arrays
let x = stockHistory.map(ph => ph.time);
let y = stockHistory.map(ph => ph.close);

// Cria gráfico inicial
Plotly.newPlot(container, [{
    x: x,
    y: y,
    mode: "lines",
    name: ticker,
    line: { color: "#007bff" }
}], {
    margin: { t: 20 },
    xaxis: { title: "Data" },
    yaxis: { title: "Preço (R$)" }
}, { responsive: true });

// Conecta ao SocketIO
const socket = io(); // Conexão automática com o servidor

// Atualizações do stock
socket.on("stocks_update", data => {
    const stock = data.stocks.find(s => s.ticker === ticker);
    if (!stock) return;

    const newDate = stock.date || new Date().toISOString(); // use stock.date se disponível
    const newPrice = stock.price;

    // Atualiza gráfico
    x.push(newDate);
    y.push(newPrice);
    Plotly.extendTraces(container, { x: [[newDate]], y: [[newPrice]] }, [0]);

    const maxPoints = 100;
    if (x.length > maxPoints) {
        x.shift();
        y.shift();
        Plotly.relayout(container, { xaxis: { range: [x[0], x[x.length - 1]] } });
    }

    // Atualiza valores principais da página
    document.querySelector("#stock-detail .text-gray-800").textContent = `R$ ${newPrice.toFixed(2)}`;

    const changePctEl = document.querySelector("#stock-detail .font-medium");
    const changeValue = stock.price - stock.open;
    changePctEl.textContent = `${((changeValue / stock.open) * 100).toFixed(2)}% (R$ ${changeValue.toFixed(2)})`;
    changePctEl.className = changeValue < 0 ? "text-red-500 font-medium" : "text-green-500 font-medium";

    const changePctEl2 = document.getElementById("stock-change");
    changePctEl2.textContent = `${((changeValue / stock.open) * 100).toFixed(2)}%`;
    changePctEl2.className = changeValue < 0 ? "text-red-500 font-bold" : "text-green-500 font-bold";

    // Atualiza Volume, Mín e Máx do Dia
    document.querySelector("#stock-detail div.border:nth-child(1) p.font-bold").textContent = stock.volume;
    document.querySelector("#stock-detail div.border:nth-child(3) p.font-bold").textContent = `R$ ${stock.low.toFixed(2)}`;
    document.querySelector("#stock-detail div.border:nth-child(4) p.font-bold").textContent = `R$ ${stock.high.toFixed(2)}`;
});
