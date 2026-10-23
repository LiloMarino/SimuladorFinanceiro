import { actionLabel, plural } from "@/shared/lib/strategy-orders";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { StrategyGroup, StrategyOrderStatus, StrategyPanel } from "@/types";

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

export const GROUP_LABEL: Record<StrategyGroup, string> = { reference: "Referência", tactic: "Tática" };
