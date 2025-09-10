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
    stocks.forEach(stock => {
        let card = container.querySelector(`[data-ticker="${stock.ticker}"]`);
        
        if (!card) {
            // se não existir, cria novo card com data-ticker
            card = createStockCard(stock);
            container.appendChild(card);
        } else {
            // atualiza valores no card já existente
            card.querySelector(".price").innerText = "R$ " + stock.price.toFixed(2);
            card.querySelector(".low").innerText = "R$ " + stock.low.toFixed(2);
            card.querySelector(".high").innerText = "R$ " + stock.high.toFixed(2);
            const changeElem = card.querySelector(".change");
            changeElem.innerText = stock.change_pct;
            changeElem.className = stock.change_pct.includes("-")
                ? "change text-red-500 text-sm font-medium"
                : "change text-green-500 text-sm font-medium";
        }
    });
}

// Escuta os eventos do backend
socket.on("stocks_update", (data) => {
    updateStocks(data.stocks);
});