const socket = window.socket;
const container = document.getElementById("stocks-container");
const template = document.getElementById("stock-card-template");

function createStockCard(stock) {
    const card = template.content.cloneNode(true);

    card.querySelector(".ticker").innerText = stock.ticker;
    card.querySelector(".name").innerText = stock.name;
    card.querySelector(".price").innerText = "R$ " + stock.price.toFixed(2);
    card.querySelector(".low").innerText = "R$ " + stock.low.toFixed(2);
    card.querySelector(".high").innerText = "R$ " + stock.high.toFixed(2);
    card.querySelector(".change").innerText = stock.change_pct;
    card.querySelector(".change").className = stock.change_pct.includes("-")
        ? "change text-red-500 text-sm font-medium"
        : "change text-green-500 text-sm font-medium";

    const detailsLink = card.querySelector(".details-link");
    detailsLink.href = `/variable_income/${stock.ticker}`;

    return card;
}

// Atualiza todos os cards
function updateStocks(stocks) {
    container.innerHTML = ""; // limpa cards antigos
    stocks.forEach(stock => {
        const card = createStockCard(stock);
        container.appendChild(card);
    });
}

// Escuta os eventos do backend
socket.on("stocks_update", (data) => {
    updateStocks(data.stocks);
});

socket.on("simulation_update", (data) => {
    const dateElem = document.getElementById("current-date");
    if (dateElem) dateElem.innerText = data.current_date;
});

socket.on("speed_update", (data) => {
    const speedElem = document.getElementById("speed");
    if (speedElem) speedElem.innerText = data.speed + "x";
});
