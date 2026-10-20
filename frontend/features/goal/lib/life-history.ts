import { ArrowDown, ArrowDownLeft, ArrowUp, Briefcase, HeartPulse, Wrench, Zap, type LucideIcon } from "lucide-react";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { displayMonthName } from "@/shared/lib/utils/display";
import type { LifeHistoryKind, LifeHistoryRow } from "@/types";

type KindInfo = {
  tag: string;
  badge: "warning" | "secondary" | "destructive";
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
};

// Ícone do imprevisto pela chave que o servidor sorteia
const UNEXPECTED_ICONS: Record<string, LucideIcon> = {
  REPAIR: Wrench,
  HEALTH: HeartPulse,
};

export function lifeRowIcon(row: LifeHistoryRow) {
  return (row.life_event_key && UNEXPECTED_ICONS[row.life_event_key]) || LIFE_HISTORY_KINDS[row.kind].icon;
}

/** O texto da coluna "O que foi"; os juros citam a taxa mensal do cheque especial da partida. */
export function lifeRowText(row: LifeHistoryRow, overdraftMonthlyRate: string) {
  switch (row.kind) {
    case "UNEXPECTED_EXPENSE":
      return row.label ?? LIFE_HISTORY_KINDS.UNEXPECTED_EXPENSE.tag;
    case "LAYOFF":
      return `Salário de ${displayMonthName(row.event_date, 1)} não entrou`;
    case "OVERDRAFT_STARTED":
      return "Caixa ficou negativo";
    case "OVERDRAFT_ENDED":
      return "Caixa voltou ao positivo";
    case "OVERDRAFT_INTEREST":
      return `Juros de ${displayRatePercent(overdraftMonthlyRate)} ao mês`;
  }
}
