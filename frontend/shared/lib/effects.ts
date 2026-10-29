import { displayMonthShort } from "@/shared/lib/utils/display";
import type { EffectPhase } from "@/types";

const MINUS = "−";

/** O texto de uma fase do efeito na inflação, com o mês em que muda. */
export function phaseText(phase: EffectPhase, peakOn: string, fadedOn: string) {
  switch (phase) {
    case "WAITING":
      return `esperando valer: cheio em ${displayMonthShort(peakOn)}`;
    case "RISING":
      return `chegando: cheio em ${displayMonthShort(peakOn)}`;
    case "FALLING":
      return `caindo: some em ${displayMonthShort(fadedOn)}`;
    case "FADED":
      return "já sumiu";
  }
}

/** A fase curta da linha do cartão de gasto. */
export const PHASE_SHORT: Record<EffectPhase, string> = {
  WAITING: "esperando valer",
  RISING: "chegando",
  FALLING: "caindo",
  FADED: "sumiu",
};

/** Pontos de IPCA com sinal e duas casas: 0.55 → "+0,55", 0 → "—". */
export function signedIpca(points: string | number) {
  const value = Number(points);
  if (Math.abs(value) < 0.005) return "—";
  return `${value > 0 ? "+" : MINUS}${Math.abs(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/** Percentual com sinal e uma casa: 0.024 → "+2,4%". */
export function signedStocks(fraction: string | number) {
  const value = Number(fraction);
  if (Math.abs(value) < 0.0005) return "—";
  return `${value > 0 ? "+" : MINUS}${Math.abs(value * 100).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
}

/** Inflação a mais pesa em vermelho, a menos em verde: os pontos de IPCA são custo para quem lê a conta. */
export function inflationTone(points: string | number): "destructive" | "success" | "default" {
  const value = Number(points);
  if (Math.abs(value) < 0.005) return "default";
  return value > 0 ? "destructive" : "success";
}

/** O traçado de uma curva em `width` × `height`, com a linha do zero dentro da área; nulo com menos de dois pontos. */
export function curvePath(values: number[], width: number, height: number, pad = 3) {
  if (values.length < 2) return null;
  const high = Math.max(0, ...values);
  const low = Math.min(0, ...values);
  const span = high - low || 1;
  const x = (index: number) => (index / (values.length - 1)) * width;
  const y = (value: number) => pad + ((high - value) / span) * (height - 2 * pad);
  const line = values.map((value, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(1)} ${y(value).toFixed(1)}`);
  return { line: line.join(" "), zero: y(0) };
}
