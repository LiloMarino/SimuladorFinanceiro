import { displayMoneyCompact, displayNumber, displayShortDate } from "@/shared/lib/utils/display";
import type { Achievement, AchievementCategory } from "@/types";

export const CATEGORY_LABELS: Record<AchievementCategory, string> = {
  FIRST_STEPS: "Primeiros passos",
  WEALTH: "Patrimônio",
  MARKET: "Mercado",
  MATCH: "Partida",
  SECRET: "Secretas",
};

type Progress = NonNullable<Achievement["progress"]>;
type Unlock = NonNullable<Achievement["unlock"]>;

/** Quanto da meta já foi cumprido, de 0 a 1. */
export function progressFraction({ current, goal }: Progress) {
  return Math.min(Number(current) / Number(goal), 1);
}

/** "R$ 642 mil de R$ 1 mi", "5 de 12 meses". */
export function displayProgress({ current, goal, unit }: Progress) {
  switch (unit) {
    case "BRL":
      return `${displayMoneyCompact(current)} de ${displayMoneyCompact(goal)}`;
    case "COUNT":
      return `${displayNumber(current, 0)} de ${displayNumber(goal, 0)}`;
    case "MONTHS":
      return `${displayNumber(current, 0)} de ${displayNumber(goal, 0)} meses`;
    case "DAYS":
      return `${displayNumber(current, 0)} de ${displayNumber(goal, 0)} dias`;
    case "POINTS":
      return `${displayNumber(current, 0)} de ${displayNumber(goal, 0)} pontos`;
  }
}

const TIME_FORMAT = new Intl.DateTimeFormat("pt-BR", {
  hour: "2-digit",
  minute: "2-digit",
});

/** A data real do desbloqueio: "hoje, 20:40" no mesmo dia, "15 out 2026" nos outros. */
export function displayUnlockedAt({ unlocked_at }: Unlock) {
  const date = new Date(unlocked_at);
  if (date.toDateString() === new Date().toDateString()) return `hoje, ${TIME_FORMAT.format(date)}`;
  return displayShortDate(date);
}

/** "15 out 2026, 22:31", para a dica do mouse. */
export function displayUnlockedMoment(unlock: Unlock) {
  const date = new Date(unlock.unlocked_at);
  return `${displayShortDate(date)}, ${TIME_FORMAT.format(date)}`;
}

/** A versão curta do progresso: "64%" para dinheiro, "62/100" para contagens. */
export function displayProgressShort(progress: Progress) {
  if (progress.unit === "BRL") return `${Math.round(progressFraction(progress) * 100)}%`;
  return `${displayNumber(progress.current, 0)}/${displayNumber(progress.goal, 0)}`;
}
