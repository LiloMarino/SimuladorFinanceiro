import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
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
    count("take_loan") > 0 && plural(count("take_loan"), "empréstimo", "empréstimos"),
    count("prepay_loan") > 0 && plural(count("prepay_loan"), "amortização", "amortizações"),
    count("payoff_loan") > 0 && plural(count("payoff_loan"), "quitação", "quitações"),
    count("pay_overdue") > 0 && plural(count("pay_overdue"), "pagamento de atraso", "pagamentos de atraso"),
  ].filter((part): part is string => !!part);
  return parts.length > 1 ? `${parts.slice(0, -1).join(", ")} e ${parts[parts.length - 1]}` : (parts[0] ?? "");
}

const CREDIT_ACTIONS: readonly StrategyAction[] = ["take_loan", "prepay_loan", "payoff_loan", "pay_overdue"];

/** Linha de crédito: sem ativo, o valor fica em `price`; juro e prazo na contratação, número do empréstimo nas demais. */
type CreditLine = Pick<StrategyOrderLine, "action" | "price" | "annual_rate" | "term_months" | "loan_number">;

export const isCreditAction = (action: StrategyAction) => CREDIT_ACTIONS.includes(action);

/** "Empréstimo · R$ 20.000,00 em 48x · 15,3% a.a.", "Quitação do empréstimo nº 2"... */
export function creditTitle({ action, price, annual_rate, term_months, loan_number }: CreditLine) {
  const amount = price === null ? "" : displayMoney(price);
  const loan = loan_number === null ? "empréstimo" : `empréstimo nº ${loan_number}`;
  switch (action) {
    case "take_loan":
      return [
        "Empréstimo",
        `${amount} em ${term_months ?? "—"}x`,
        annual_rate === null ? null : `${displayPercent(annual_rate, 2, { trim: true })} a.a.`,
      ]
        .filter(Boolean)
        .join(" · ");
    case "prepay_loan":
      return `Amortização de ${amount} no ${loan}`;
    case "payoff_loan":
      return `Quitação do ${loan}`;
    default:
      return `Atraso pago do ${loan}`;
  }
}

/** O verbo da ordem no aviso: "A estratégia comprou 300 PETR4". */
export function orderToastTitle(order: StrategyOrderLine) {
  if (isCreditAction(order.action))
    return order.status === "refused" ? `Recusada: ${creditTitle(order)}` : creditTitle(order);
  const what = order.ticker ?? order.asset_name ?? "";
  const quantity = order.quantity === null ? "" : `${displayQuantity(order.quantity)} `;
  const verb = {
    buy: "comprou",
    sell: "vendeu",
    cancel: "cancelou a ordem de",
    invest: "aplicou em",
    redeem: "resgatou de",
    take_loan: "tomou",
    prepay_loan: "amortizou",
    payoff_loan: "quitou",
    pay_overdue: "pagou o atraso de",
  }[order.action];
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
  take_loan: "text-primary",
  prepay_loan: "text-primary",
  payoff_loan: "text-primary",
  pay_overdue: "text-primary",
};

const ACTION_LABEL: Record<StrategyAction, string> = {
  buy: "Comprou",
  sell: "Vendeu",
  cancel: "Cancelou",
  invest: "Aplicou",
  redeem: "Resgatou",
  take_loan: "Empréstimo",
  prepay_loan: "Amortização",
  payoff_loan: "Quitação",
  pay_overdue: "Atraso pago",
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
  return row.quantity === null ? "—" : displayQuantity(row.quantity);
}

/** Preço da linha: "lim. R$ 18,40" enquanto a ordem limitada não executou por inteiro. */
export function rowPrice(row: StrategyLogRow) {
  if (row.price === null) return "—";
  const limited = row.order_type === "limit" && row.status !== "executed";
  return `${limited ? "lim. " : ""}${displayMoney(row.price)}`;
}
