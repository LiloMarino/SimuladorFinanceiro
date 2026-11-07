import { displayCompactNumber, displayMoney, displayNumber } from "@/shared/lib/utils/display";
import type { TechnicalIndicators } from "@/types";

export const TIME_SCALES = ["1s", "1m", "3m", "1a", "3a", "5a", "MAX"] as const;
export const SCALE_LABELS: Record<TimeScale, string> = {
  "1s": "1S",
  "1m": "1M",
  "3m": "3M",
  "1a": "1A",
  "3a": "3A",
  "5a": "5A",
  MAX: "Tudo",
};
export const SCALE_DAYS: Record<TimeScale, number | null> = {
  "1s": 7, // 7 dias
  "1m": 30, // 1 mês
  "3m": 90, // 3 meses
  "1a": 365, // 1 ano
  "3a": 3 * 365,
  "5a": 5 * 365,
  MAX: null, // Tudo
} as const;

export const PRICE_HEIGHT = 360;
export const POP_WIDTH = 200;
export const CARD_WIDTH = 320;
// O eixo de tempo fica fora dos painéis: somado à altura, cada painel recebe exatamente a sua
export const TIME_AXIS_HEIGHT = 28;
// Com muitos painéis, cada um encolhe para o preço seguir legível
export const paneHeight = (panels: number) => (panels <= 3 ? 90 : 60);

// O preço sai em reais; volume e OBV, em número curto
export const MONEY_FORMAT = {
  type: "custom",
  minMove: 0.01,
  formatter: displayMoney,
} as const;
export const VOLUME_FORMAT = {
  type: "custom",
  minMove: 1,
  formatter: displayCompactNumber,
} as const;
export const NUMBER_FORMAT = {
  type: "custom",
  minMove: 0.01,
  formatter: (value: number) => displayNumber(value),
} as const;
export const ZERO_TO_HUNDRED = () => ({ priceRange: { minValue: 0, maxValue: 100 } });

export type TimeScale = (typeof TIME_SCALES)[number];
export type ChartType = "line" | "candle";
export type Series = TechnicalIndicators["series"];

/** O dia sob a mira, com a posição dela no gráfico e a largura dele. */
export type CrosshairHover = { day: string; x: number; width: number };

// Séries antes de o cálculo chegar: todos os indicadores ausentes
export const NO_SERIES: Series = {
  averages: null,
  bollinger: null,
  rsi: null,
  macd: null,
  stochastic: null,
  atr: null,
  obv: null,
};
