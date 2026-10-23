import { displayMoney } from "@/shared/lib/utils/display";
import type { StrategyAction, StrategyLogRow, StrategyOrderLine } from "@/types";

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
    count("redeem") > 0 && plural(count("redeem"), "resgate", "resgates"),
    count("cancel") > 0 && plural(count("cancel"), "cancelamento", "cancelamentos"),
  ].filter((part): part is string => !!part);
  return parts.length > 1 ? `${parts.slice(0, -1).join(", ")} e ${parts[parts.length - 1]}` : (parts[0] ?? "");
}

/** O verbo da ordem no aviso: "A estratégia comprou 300 PETR4". */
export function orderToastTitle(order: StrategyOrderLine) {
  const what = order.ticker ?? order.asset_name ?? "";
  const quantity = order.quantity === null ? "" : `${order.quantity} `;
  const verb = { buy: "comprou", sell: "vendeu", cancel: "cancelou a ordem de", invest: "aplicou em", redeem: "resgatou de" }[order.action];
  return order.status === "refused"
    ? `A estratégia tentou ${order.action === "buy" ? "comprar" : order.action === "sell" ? "vender" : "operar"} ${quantity}${what}`
    : `A estratégia ${verb} ${quantity}${what}`.trim();
}

/** Cor do verbo da ordem no registro. */
export const ACTION_TONE: Record<StrategyAction, string> = {
  buy: "text-success",
  sell: "text-destructive",
  cancel: "text-muted-foreground",
  invest: "text-primary",
  redeem: "text-foreground",
};

const ACTION_LABEL: Record<StrategyAction, string> = {
  buy: "Comprou",
  sell: "Vendeu",
  cancel: "Cancelou",
  invest: "Aplicou",
  redeem: "Resgatou",
};

export function actionLabel(action: StrategyAction) {
  return ACTION_LABEL[action];
}

/** Quanto do caixa cada compra usa: `percent`% do caixa de hoje. */
export function cashShare(cash: string | number, percent: number) {
  return (Number(cash) * percent) / 100;
}

/** Quantidade da linha do registro: renda fixa não tem, e a recusada mostra o que pediu. */
export function rowQuantity(row: StrategyLogRow) {
  return row.quantity === null ? "—" : row.quantity.toLocaleString("pt-BR");
}

/** Preço da linha: "lim. R$ 18,40" enquanto a ordem limitada não executou por inteiro. */
export function rowPrice(row: StrategyLogRow) {
  if (row.price === null) return "—";
  const limited = row.order_type === "limit" && row.status !== "executed";
  return `${limited ? "lim. " : ""}${displayMoney(row.price)}`;
}
