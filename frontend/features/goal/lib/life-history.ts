import {
  ArrowDown,
  ArrowDownLeft,
  ArrowUp,
  Briefcase,
  HeartPulse,
  Landmark,
  Percent,
  ReceiptText,
  TrendingUp,
  Wrench,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { displayMonthName } from "@/shared/lib/utils/display";
import type { LifeHistoryKind, LifeHistoryRow } from "@/types";

type KindInfo = {
  tag: string;
  badge: "warning" | "secondary" | "destructive" | "info";
  icon: LucideIcon;
};

/** Como cada tipo de linha do histórico se mostra: a etiqueta da coluna "Tipo" e o ícone. */
export const LIFE_HISTORY_KINDS: Record<LifeHistoryKind, KindInfo> = {
  UNEXPECTED_EXPENSE: { tag: "Imprevisto", badge: "warning", icon: Zap },
  LAYOFF: { tag: "Demissão", badge: "destructive", icon: Briefcase },
  OVERDRAFT_STARTED: {
    tag: "Cheque especial",
    badge: "secondary",
    icon: ArrowDown,
  },
  OVERDRAFT_ENDED: {
    tag: "Cheque especial",
    badge: "secondary",
    icon: ArrowUp,
  },
  OVERDRAFT_INTEREST: {
    tag: "Cheque especial",
    badge: "secondary",
    icon: ArrowDownLeft,
  },
  SALARY_READJUSTED: { tag: "Salário", badge: "info", icon: TrendingUp },
  EXPENSE_READJUSTED: { tag: "Despesa", badge: "info", icon: ReceiptText },
  SALARY_TAX_CHANGED: { tag: "Salário", badge: "info", icon: Landmark },
  OVERDRAFT_RATE_CHANGED: { tag: "Cheque especial", badge: "info", icon: Percent },
};

// Ícone do imprevisto pela chave que o servidor sorteia
const UNEXPECTED_ICONS: Record<string, LucideIcon> = {
  REPAIR: Wrench,
  HEALTH: HeartPulse,
};

export function lifeRowIcon(row: LifeHistoryRow) {
  return (row.life_event_key && UNEXPECTED_ICONS[row.life_event_key]) || LIFE_HISTORY_KINDS[row.kind].icon;
}

/** O texto da coluna "O que foi"; as mudanças do orçamento e a demissão trazem a origem na economia da partida. */
export function lifeRowText(row: LifeHistoryRow) {
  switch (row.kind) {
    case "UNEXPECTED_EXPENSE":
      return row.label ?? LIFE_HISTORY_KINDS.UNEXPECTED_EXPENSE.tag;
    case "LAYOFF":
      return `Salário de ${displayMonthName(row.event_date, 1)} não entrou${row.label ? ` · ${row.label}` : ""}`;
    case "OVERDRAFT_STARTED":
      return "Caixa ficou negativo";
    case "OVERDRAFT_ENDED":
      return "Caixa voltou ao positivo";
    case "OVERDRAFT_INTEREST":
      return "Juros do cheque especial";
    case "SALARY_READJUSTED":
    case "EXPENSE_READJUSTED":
    case "SALARY_TAX_CHANGED":
    case "OVERDRAFT_RATE_CHANGED":
      return row.label ?? LIFE_HISTORY_KINDS[row.kind].tag;
  }
}
