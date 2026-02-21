import type { Order, OrderAction, StockDetails } from "@/types";

export class VariableIncomeStock {
    readonly stock: StockDetails;
    readonly pendingOrders: Order[];

    constructor(
        stock: StockDetails,
        pendingOrders: Order[],
    ) {
        this.stock = stock;
        this.pendingOrders = pendingOrders;
    }

    get ticker(): string {
        return this.stock.ticker;
    }

    get close(): number {
        return this.stock.close;
    }

    get best_buy(): number | null {
        const buyPrices = this.pendingOrders
            .filter((order) => order.action === "buy" && (order.status === "pending" || order.status === "partial"))
            .map((order) => order.limit_price)
            .filter((price): price is number => price !== null);

        if (buyPrices.length === 0) {
            return null;
        }

        return Math.max(...buyPrices);
    }

    get best_sell(): number | null {
        const sellPrices = this.pendingOrders
            .filter((order) => order.action === "sell" && (order.status === "pending" || order.status === "partial"))
            .map((order) => order.limit_price)
            .filter((price): price is number => price !== null);

        if (sellPrices.length === 0) {
            return null;
        }

        return Math.min(...sellPrices);
    }

    getMarketPrice(action: OrderAction): number | null {
        return action === "buy" ? this.best_sell : this.best_buy;
    }
}
