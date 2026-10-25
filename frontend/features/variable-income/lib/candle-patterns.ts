import type { CandlePattern, CandlePatternCode } from "@/types";

/** Uma vela do desenho do padrão, em preços de 0 (embaixo) a 100 (no alto). */
export interface DrawnCandle {
  open: number;
  close: number;
  high: number;
  low: number;
}

export type PatternSide = CandlePattern["direction"];

export interface PatternInfo {
  name: string;
  /** O nome com a preposição, para a frase seguir o gênero ("do martelo", "da estrela cadente"). */
  of: string;
  side: PatternSide;
  /** O que a forma conta sobre quem estava no comando do pregão. */
  summary: string;
  candles: DrawnCandle[];
}

const bullish = (low: number, open: number, close: number, high: number): DrawnCandle => ({ open, close, high, low });
const bearish = (low: number, close: number, open: number, high: number): DrawnCandle => ({ open, close, high, low });

export const PATTERN_INFO: Record<CandlePatternCode, PatternInfo> = {
  hammer: {
    name: "Martelo",
    of: "do martelo",
    side: "up",
    summary:
      "Corpo pequeno no alto e sombra de baixo pelo menos duas vezes maior, depois de uma queda: os vendedores empurraram o preço para baixo, mas os compradores o trouxeram de volta.",
    candles: [bullish(18, 76, 88, 90)],
  },
  inverted_hammer: {
    name: "Martelo invertido",
    of: "do martelo invertido",
    side: "up",
    summary:
      "Corpo pequeno embaixo e sombra de cima pelo menos duas vezes maior, depois de uma queda: os compradores testaram o preço para cima pela primeira vez.",
    candles: [bullish(10, 12, 24, 82)],
  },
  hanging_man: {
    name: "Enforcado",
    of: "do enforcado",
    side: "down",
    summary:
      "O formato do martelo depois de uma alta: o preço caiu forte no meio do pregão e voltou, o que pode avisar que os compradores estão cansando.",
    candles: [bearish(18, 76, 88, 90)],
  },
  shooting_star: {
    name: "Estrela cadente",
    of: "da estrela cadente",
    side: "down",
    summary:
      "Corpo pequeno embaixo e sombra de cima longa, depois de uma alta: os compradores subiram o preço, mas os vendedores o devolveram.",
    candles: [bearish(10, 12, 24, 82)],
  },
  doji: {
    name: "Doji",
    of: "do doji",
    side: "neutral",
    summary:
      "Abriu e fechou quase no mesmo preço: compradores e vendedores empataram no pregão. Indecisão, sem lado sugerido.",
    candles: [bullish(14, 49, 51, 86)],
  },
  bullish_engulfing: {
    name: "Engolfo de alta",
    of: "do engolfo de alta",
    side: "up",
    summary:
      "Uma vela de alta que cobre por inteiro a vela de baixa do dia anterior: os compradores tomaram o controle.",
    candles: [bearish(38, 46, 62, 66), bullish(32, 40, 72, 76)],
  },
  bearish_engulfing: {
    name: "Engolfo de baixa",
    of: "do engolfo de baixa",
    side: "down",
    summary:
      "Uma vela de baixa que cobre por inteiro a vela de alta do dia anterior: os vendedores tomaram o controle.",
    candles: [bullish(38, 46, 62, 66), bearish(28, 28, 68, 72)],
  },
  morning_star: {
    name: "Estrela da manhã",
    of: "da estrela da manhã",
    side: "up",
    summary:
      "Uma vela de baixa grande, um dia de indecisão e uma vela de alta que recupera mais da metade da primeira: a queda perdeu força.",
    candles: [bearish(40, 46, 84, 88), bearish(28, 34, 40, 44), bullish(32, 40, 78, 82)],
  },
  evening_star: {
    name: "Estrela da tarde",
    of: "da estrela da tarde",
    side: "down",
    summary:
      "Uma vela de alta grande, um dia de indecisão e uma vela de baixa que devolve mais da metade da primeira: a alta perdeu força.",
    candles: [bullish(16, 20, 56, 60), bullish(60, 62, 72, 76), bearish(22, 26, 70, 74)],
  },
  three_white_soldiers: {
    name: "Três soldados brancos",
    of: "dos três soldados brancos",
    side: "up",
    summary: "Três velas de alta seguidas, cada uma fechando mais alto que a anterior: compra firme por três pregões.",
    candles: [bullish(14, 18, 40, 44), bullish(32, 36, 60, 64), bullish(50, 54, 82, 86)],
  },
  three_black_crows: {
    name: "Três corvos negros",
    of: "dos três corvos negros",
    side: "down",
    summary: "Três velas de baixa seguidas, cada uma fechando mais baixo que a anterior: venda firme por três pregões.",
    candles: [bearish(50, 54, 82, 86), bearish(32, 36, 64, 68), bearish(14, 18, 46, 50)],
  },
};

/** O lado em palavras curtas, para o chip ao lado do nome. */
export const SIDE_LABEL: Record<PatternSide, { card: string; list: string }> = {
  up: { card: "sugere alta", list: "alta" },
  down: { card: "sugere baixa", list: "baixa" },
  neutral: { card: "indecisão", list: "indecisão" },
};

/** Estatística do padrão que a amostra sustenta: com menos de 10 ocorrências não sai percentual. */
export const MIN_SAMPLE = 10;
