import { displayPoints } from "@/shared/lib/budget-metrics";
import type { GovernmentMonetary } from "@/types";

// Os grupos de eleitores aceitam o juro real nessa faixa, em pontos percentuais
const REAL_RATE_BAND = { low: 2, high: 7 } as const;

/** Fração em pontos percentuais, sem ruído de ponto flutuante: "0.1075" → 10.75. */
export const toPoints = (fraction: string | number) => Math.round(Number(fraction) * 10_000) / 100;

/**
 * A janela do controle da SELIC, nos passos de 0,25 que a reunião alcança. A SELIC de hoje é a
 * efetiva (13,65% com a meta em 13,75%), fora da grade: a janela fica nos passos dentro do teto
 * dela, sem passar de zero, sempre alcança o passo mais próximo da SELIC da história de hoje, e
 * o controle começa no passo mais próximo da SELIC de hoje.
 */
export function selicWindow(monetary: GovernmentMonetary) {
  // Em centésimos de ponto, inteiros, para a grade não sofrer com ponto flutuante
  const selic = Math.round(toPoints(monetary.selic) * 100);
  const cap = Math.round(toPoints(monetary.cap) * 100);
  const step = Math.round(toPoints(monetary.step) * 100);
  const history = Math.round(Math.round(toPoints(monetary.history_selic) * 100) / step) * step;
  const min = Math.max(0, Math.min(Math.ceil((selic - cap) / step) * step, history));
  const max = Math.max(Math.floor((selic + cap) / step) * step, history);
  const nearest = Math.min(max, Math.max(min, Math.round(selic / step) * step));
  return { min: min / 100, max: max / 100, step: step / 100, selic: selic / 100, nearest: nearest / 100 };
}

/** "−0,50 ponto", "mantém" ou "+0,75 ponto": o quanto a decisão marcada mexe na SELIC de hoje. */
export function moveLabel(planned: number, selic: number) {
  const move = Math.round((planned - selic) * 100) / 100;
  if (move === 0) return "mantém";
  return `${move > 0 ? "+" : "−"}${displayPoints(Math.abs(move), 2)}`;
}

/** Fora da faixa dos grupos, o juro real pesa na aprovação: abaixo, de quem poupa; acima, de quem toma crédito. */
export function realRateTone(realRate: string): "default" | "warning" {
  const points = toPoints(realRate);
  return points < REAL_RATE_BAND.low || points > REAL_RATE_BAND.high ? "warning" : "default";
}

/** Abaixo de 50 a credibilidade já pesa no prêmio e na inflação; abaixo de 80, merece atenção. */
export function credibilityTone(credibility: number): "default" | "warning" | "destructive" {
  if (credibility < 50) return "destructive";
  return credibility < 80 ? "warning" : "default";
}

/** Quem lê o juro real de hoje perde aprovação, ou ninguém. */
export function realRateReading(realRate: string) {
  const points = toPoints(realRate);
  if (points < REAL_RATE_BAND.low) return "Abaixo de 2%: aposentados e investidores reclamam.";
  if (points > REAL_RATE_BAND.high) return "Acima de 7%: trabalhadores com carteira e empreendedores reclamam.";
  return "Entre 2% e 7%: nenhum grupo reclama do juro.";
}
