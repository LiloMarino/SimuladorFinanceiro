import { plural } from "@/shared/lib/strategy-orders";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { StrategyAction, StrategyGroup, StrategyLogRow, StrategyOrderStatus, StrategyPanel } from "@/types";

const ACTION_LABEL: Record<StrategyAction, string> = {
  buy: "Comprou",
  sell: "Vendeu",
  cancel: "Cancelou",
  invest: "Aplicou",
};

export function actionLabel(action: StrategyAction) {
  return ACTION_LABEL[action];
}

/** Situação da ordem na tabela do registro: o rótulo e o tom do selo. */
export const STATUS_BADGE: Record<
  StrategyOrderStatus,
  { label: string; variant: "success" | "warning" | "info" | "secondary" | "destructive" }
> = {
  executed: { label: "Executada", variant: "success" },
  partial: { label: "Parcial", variant: "warning" },
  open: { label: "Aberta", variant: "info" },
  canceled: { label: "Cancelada", variant: "secondary" },
  refused: { label: "Recusada", variant: "destructive" },
};

/** "11 executadas, 2 abertas, 1 cancelada": as situações que têm alguma ordem. */
export function ordersBreakdown(panel: StrategyPanel) {
  const parts = [
    panel.executed > 0 && plural(panel.executed, "executada", "executadas"),
    panel.partial > 0 && plural(panel.partial, "parcial", "parciais"),
    panel.open > 0 && plural(panel.open, "aberta", "abertas"),
    panel.canceled > 0 && plural(panel.canceled, "cancelada", "canceladas"),
    panel.refused > 0 && plural(panel.refused, "recusada", "recusadas"),
  ].filter(Boolean);
  return parts.length > 0 ? parts.join(", ") : "Nenhuma ordem ainda";
}

/** "Vendeu 200 VALE3", ou o título aplicado na renda fixa. */
export function lastOrderTitle(last: NonNullable<StrategyPanel["last_order"]>) {
  const what = last.ticker ?? last.asset_name ?? "";
  const quantity = last.quantity === null ? "" : `${last.quantity} `;
  return `${actionLabel(last.action)} ${quantity}${what}`.trim();
}

/** "Hoje, 14 mar, a mercado" / "12 mar, limitada". */
export function lastOrderWhen(last: NonNullable<StrategyPanel["last_order"]>, currentDate: string | undefined) {
  const day = displayDayMonth(last.order_date);
  const when = last.order_date === currentDate ? `Hoje, ${day}` : day;
  const kind = last.order_type === "limit" ? "limitada" : last.order_type === "market" ? "a mercado" : null;
  return kind ? `${when}, ${kind}` : when;
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

export const GROUP_LABEL: Record<StrategyGroup, string> = { reference: "Referência", tactic: "Tática" };

/** Título e dica de cada grupo na lista de estratégias. */
export const GROUP_SECTION: Record<StrategyGroup, { title: string; hint: string }> = {
  reference: {
    title: "Referências",
    hint: "Estratégias simples, sem parâmetros de risco, que servem de régua: se a sua não rende mais do que elas, o trabalho extra não compensou.",
  },
  tactic: {
    title: "Táticas",
    hint: "Regras que reagem ao preço e escolhem quando comprar e vender. Têm parâmetros que você ajusta e vê no gráfico antes de salvar.",
  },
};

/** Explicação do termo técnico que a regra de cada estratégia usa. */
export const TERM_HINT: Record<string, string> = {
  cdi_100:
    "CDI é a taxa de juros que os bancos cobram entre si, a régua da renda fixa. Um título que paga 100% do CDI rende o mesmo que ela; 110% rende 10% a mais.",
  moving_average_cross:
    "Média móvel é o preço médio dos últimos N pregões. Ex.: a média de 50 dias a R$ 32 cruzando para cima a de 200 dias a R$ 31 mostra que a alta recente ficou mais forte que a tendência longa: sinal de compra.",
};
