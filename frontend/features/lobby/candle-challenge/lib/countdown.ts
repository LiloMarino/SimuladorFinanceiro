/** Segundos inteiros que faltam, arredondados para cima: "0 s" só quando o tempo acabou. */
export function secondsLeft(remainingMs: number) {
  return Math.max(0, Math.ceil(remainingMs / 1000));
}

/** Nos 2 segundos finais a barra fica vermelha. */
const URGENT_MS = 2000;

export function isUrgent(remainingMs: number) {
  return remainingMs <= URGENT_MS;
}

/** Quanto da barra ainda está cheia, de 0 a 1. */
export function timeFraction(remainingMs: number, durationMs: number) {
  if (durationMs <= 0) return 0;
  return Math.min(1, Math.max(0, remainingMs / durationMs));
}
