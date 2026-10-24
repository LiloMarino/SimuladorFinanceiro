import { parseLocalDate } from "@/shared/lib/utils/display";

// Medido no app: 2 estratégias levam ~28 ms por pregão e 10 levam ~54 ms (uma base fixa mais um custo por estratégia)
const BASE_SECONDS_PER_DAY = 0.022;
const SECONDS_PER_DAY_PER_STRATEGY = 0.0032;

/** Pregões do menor período aceito: a nota precisa de 63 (uns 3 meses). */
export const MIN_TRADING_DAYS = 63;

/** Dias úteis entre as datas (inclusive), sem descontar feriado: a estimativa do que o servidor conta. */
export function weekdaysBetween(start: string, end: string) {
  const last = parseLocalDate(end);
  let count = 0;
  for (const day = parseLocalDate(start); day <= last; day.setDate(day.getDate() + 1)) {
    const weekday = day.getDay();
    if (weekday !== 0 && weekday !== 6) count++;
  }
  return count;
}

/** "17 anos", "1 ano e 2 meses", "8 meses": o tamanho do período em palavras. */
export function displaySpan(start: string, end: string) {
  const from = parseLocalDate(start);
  const to = parseLocalDate(end);
  const months = Math.max((to.getFullYear() - from.getFullYear()) * 12 + to.getMonth() - from.getMonth() + 1, 1);
  const years = Math.floor(months / 12);
  const rest = months % 12;
  const yearsText = years === 1 ? "1 ano" : `${years} anos`;
  const restText = rest === 1 ? "1 mês" : `${rest} meses`;
  if (years === 0) return restText;
  return rest === 0 ? yearsText : `${yearsText} e ${restText}`;
}

/** Quanto o backtest leva, em palavras: "cerca de 2 minutos". */
export function displayEstimate(tradingDays: number, strategies: number) {
  const seconds = tradingDays * (BASE_SECONDS_PER_DAY + SECONDS_PER_DAY_PER_STRATEGY * strategies);
  if (seconds < 45) return "menos de 1 minuto";
  const minutes = Math.round(seconds / 60);
  return minutes <= 1 ? "cerca de 1 minuto" : `cerca de ${minutes} minutos`;
}

/** Segundos que faltam, em palavras curtas: "~40 s" ou "~2 min". */
export function displaySecondsLeft(seconds: number) {
  return seconds < 90 ? `~${Math.max(Math.round(seconds), 1)} s` : `~${Math.round(seconds / 60)} min`;
}
