import type { StrategyAction, StrategyOrderLine } from "@/types";

export function plural(count: number, one: string, many: string) {
  return `${count} ${count === 1 ? one : many}`;
}

/** "3 compras e 1 venda": o resumo do dia quando a estratégia manda muitas ordens. */
export function dayOrdersSummary(orders: StrategyOrderLine[]) {
  const count = (action: StrategyAction) => orders.filter((order) => order.action === action).length;
  const parts = [
    count("buy") > 0 && plural(count("buy"), "compra", "compras"),
    count("sell") > 0 && plural(count("sell"), "venda", "vendas"),
    count("invest") > 0 && plural(count("invest"), "aplicação", "aplicações"),
    count("cancel") > 0 && plural(count("cancel"), "cancelamento", "cancelamentos"),
  ].filter((part): part is string => !!part);
  return parts.length > 1 ? `${parts.slice(0, -1).join(", ")} e ${parts[parts.length - 1]}` : (parts[0] ?? "");
}

/** O verbo da ordem no aviso: "A estratégia comprou 300 PETR4". */
export function orderToastTitle(order: StrategyOrderLine) {
  const what = order.ticker ?? order.asset_name ?? "";
  const quantity = order.quantity === null ? "" : `${order.quantity} `;
  const verb = { buy: "comprou", sell: "vendeu", cancel: "cancelou a ordem de", invest: "aplicou em" }[order.action];
  return order.status === "refused"
    ? `A estratégia tentou ${order.action === "buy" ? "comprar" : order.action === "sell" ? "vender" : "operar"} ${quantity}${what}`
    : `A estratégia ${verb} ${quantity}${what}`.trim();
}
