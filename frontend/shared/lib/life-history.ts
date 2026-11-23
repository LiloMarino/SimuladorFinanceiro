import {
  ArrowDown,
  ArrowDownLeft,
  ArrowUp,
  Briefcase,
  Gift,
  HeartPulse,
  Landmark,
  Repeat,
  Percent,
  ReceiptText,
  TrendingUp,
  Wrench,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { PROFESSIONS } from "@/shared/lib/professions";
import { displayMonthName } from "@/shared/lib/utils/display";
import type { LifeHistoryKind, LifeHistoryRow, Profession } from "@/types";

type KindInfo = {
  tag: string;
  badge: "warning" | "secondary" | "destructive" | "info" | "success";
  icon: LucideIcon;
};

/** Como cada tipo de linha do histórico se mostra: a etiqueta da coluna "Tipo" e o ícone. */
export const LIFE_HISTORY_KINDS: Record<LifeHistoryKind, KindInfo> = {
  UNEXPECTED_EXPENSE: { tag: "Imprevisto", badge: "warning", icon: Zap },
  UNEXPECTED_INCOME: { tag: "Imprevisto", badge: "success", icon: Gift },
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
  PROFESSION_SWITCHED: { tag: "Profissão", badge: "info", icon: Repeat },
  PROFESSION_ACTION: { tag: "Profissão", badge: "info", icon: Briefcase },
  FGTS_WITHDRAWAL: { tag: "Profissão", badge: "success", icon: Landmark },
};

// O que cada ação da profissão diz no histórico, pela chave que o servidor grava
const PROFESSION_ACTION_TEXTS: Record<string, string> = {
  overtime_on: "Ligou a hora extra",
  overtime_off: "Desligou a hora extra",
  overtime_ended: "A hora extra acabou com a recessão",
  overtime_available: "A hora extra pode voltar",
  exchange_lock: "Contratou a trava de câmbio",
  exchange_lock_ended: "A trava de câmbio venceu",
  export_mix: "Mudou o mix de exportação",
};

// Ícone do imprevisto pela chave que o servidor sorteia
const UNEXPECTED_ICONS: Record<string, LucideIcon> = {
  REPAIR: Wrench,
  HEALTH: HeartPulse,
};

export function lifeRowIcon(row: LifeHistoryRow) {
  return (row.life_event_key && UNEXPECTED_ICONS[row.life_event_key]) || LIFE_HISTORY_KINDS[row.kind].icon;
}

/** O texto da coluna "O que foi"; as mudanças do orçamento e a perda de renda trazem a origem na economia da partida. */
export function lifeRowText(row: LifeHistoryRow) {
  switch (row.kind) {
    case "UNEXPECTED_EXPENSE":
    case "UNEXPECTED_INCOME":
      return row.label ?? LIFE_HISTORY_KINDS[row.kind].tag;
    case "LAYOFF":
      return `Renda de ${displayMonthName(row.event_date, 1)} não entrou${row.label ? ` · ${row.label}` : ""}`;
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
    case "PROFESSION_SWITCHED": {
      const profession = row.life_event_key && PROFESSIONS[row.life_event_key as Profession];
      return profession ? `Mudou de profissão para ${profession.name}` : "Mudou de profissão";
    }
    case "PROFESSION_ACTION":
      return (row.life_event_key && PROFESSION_ACTION_TEXTS[row.life_event_key]) || LIFE_HISTORY_KINDS[row.kind].tag;
    case "FGTS_WITHDRAWAL":
      return "Saque do FGTS com a multa de 40%";
  }
}
