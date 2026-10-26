import { displayCompactNumber, displayDecimal, displayMoney, displayNumber } from "@/shared/lib/utils/display";
import type { MetricInfo } from "@/shared/lib/metric-info";
import type {
  IndicatorKey,
  IndicatorParams,
  IndicatorSettings,
  MovingAverage,
  TechnicalReading,
  TechnicalSummary,
} from "@/types";

/** Onde o indicador é desenhado: sobre o preço ou num painel próprio embaixo do gráfico. */
export type IndicatorPlace = "price" | "panel";

export interface IndicatorInfo {
  key: IndicatorKey;
  name: string;
  description: string;
  place: IndicatorPlace;
  // Cor da linha principal (token hex do tema, o canvas lê por getComputedStyle)
  color: string | null;
  hint: MetricInfo;
  // Parâmetros resumidos à direita da linha no seletor ("12 · 26 · 9"); null sem parâmetros
  summary: ((params: IndicatorParams) => string) | null;
}

const text = (value: string | number) => String(value);

export const INDICATORS: IndicatorInfo[] = [
  {
    key: "averages",
    name: "Médias móveis",
    description: "Média do fechamento dos últimos pregões: mostra a tendência sem o sobe e desce do dia",
    place: "price",
    color: "--chart-5",
    hint: {
      label: "Médias móveis",
      description: "Média do fechamento dos últimos pregões",
      definition:
        "A média simples (MMS) soma os fechamentos dos últimos N pregões e divide por N. A exponencial (MME) dá mais peso aos dias recentes, então vira antes.",
      example: "Ex.: fechamentos de R$ 30, R$ 31 e R$ 32 dão MMS de 3 pregões de R$ 31.",
      reading:
        "Preço acima da média costuma ser lido como tendência de alta (compra); abaixo, de baixa (venda). Quando a média curta cruza a longa para cima, a alta ganha força.",
      format: text,
    },
    summary: (params) => String(params.averages.length),
  },
  {
    key: "bollinger",
    name: "Bandas de Bollinger",
    description: "Faixa onde o preço costuma ficar; sair dela é raro",
    place: "price",
    color: "--chart-2",
    hint: {
      label: "Bandas de Bollinger",
      description: "Faixa em volta da média de 20 pregões",
      definition:
        "Uma média simples com uma banda acima e outra abaixo, a 2 desvios-padrão de distância. O desvio-padrão mede o quanto o preço se afasta da média: preço agitado abre a faixa.",
      example: "Ex.: média de R$ 31,55 e desvio de R$ 0,67 dão a faixa de R$ 30,21 a R$ 32,89.",
      reading:
        "Uns 95% dos fechamentos ficam dentro da faixa. Fechar acima da banda de cima é lido como esticado demais (venda); abaixo da de baixo, como caído demais (compra).",
      format: text,
    },
    summary: (params) => `${params.bollinger_period} · ${displayDecimal(params.bollinger_deviations)}`,
  },
  {
    key: "volume",
    name: "Volume",
    description: "Quantas ações trocaram de mão no dia",
    place: "panel",
    color: null,
    hint: {
      label: "Volume",
      description: "Ações negociadas no dia",
      definition:
        "A quantidade de ações compradas e vendidas no pregão. A barra fica verde no dia de alta e vermelha no de baixa.",
      example: "Ex.: 48,2 mi quer dizer que 48,2 milhões de ações trocaram de mão.",
      reading:
        "Um movimento com volume acima do normal tem mais gente por trás e costuma ser mais confiável que um com volume baixo.",
      format: text,
    },
    summary: null,
  },
  {
    key: "rsi",
    name: "IFR · Índice de Força Relativa",
    description: "De 0 a 100: compara as altas com as baixas recentes",
    place: "panel",
    color: "--chart-6",
    hint: {
      label: "IFR · Índice de Força Relativa",
      description: "De 0 a 100: compara as altas com as baixas recentes",
      definition:
        "Compara o tamanho das altas com o das baixas nos últimos 14 pregões, numa nota de 0 a 100. Quanto mais as altas pesam, mais perto de 100.",
      example:
        "Ex.: em 14 pregões, as altas somaram R$ 2,10 e as baixas R$ 1,18. As altas foram 1,8 vez as baixas, e o IFR fica em 64.",
      reading:
        "Acima de 70, subiu rápido demais e costuma devolver (sobrecomprado, venda). Abaixo de 30, caiu rápido demais (sobrevendido, compra). Entre os dois, neutro. É uma leitura do dia, não uma previsão.",
      format: text,
    },
    summary: (params) => String(params.rsi_period),
  },
  {
    key: "macd",
    name: "MACD",
    description: "Distância entre uma média curta e uma longa: mostra se a tendência ganha ou perde força",
    place: "panel",
    color: "--chart-1-canvas",
    hint: {
      label: "MACD",
      description: "Média exponencial de 12 menos a de 26 pregões",
      definition:
        "A linha do MACD é a média exponencial de 12 pregões menos a de 26. O sinal é a média de 9 pregões dessa linha, e o histograma é a distância entre as duas.",
      example: "Ex.: MME 12 de R$ 31,80 e MME 26 de R$ 31,47 dão MACD de 0,33.",
      reading:
        "Linha acima do sinal (histograma positivo) é lida como alta ganhando força (compra); abaixo, como perdendo força (venda).",
      format: text,
    },
    summary: (params) => `${params.macd_fast} · ${params.macd_slow} · ${params.macd_signal}`,
  },
  {
    key: "stochastic",
    name: "Estocástico",
    description: "Onde o fechamento ficou entre a mínima e a máxima dos últimos pregões",
    place: "panel",
    color: "--chart-7",
    hint: {
      label: "Estocástico",
      description: "De 0 a 100: onde o fechamento ficou na faixa dos últimos pregões",
      definition:
        "O %K diz onde o fechamento ficou entre a mínima e a máxima dos últimos 14 pregões: 0 é na mínima, 100 é na máxima. O %D é a média de 3 pregões do %K.",
      example: "Ex.: mínima de R$ 29, máxima de R$ 33 e fechamento de R$ 32,50 dão %K de 87,5.",
      reading:
        "Acima de 80 é lido como sobrecomprado (venda); abaixo de 20, como sobrevendido (compra); no meio, neutro.",
      format: text,
    },
    summary: (params) => `${params.stochastic_k} · ${params.stochastic_d}`,
  },
  {
    key: "atr",
    name: "ATR",
    description: "Quanto o preço anda por dia, em reais",
    place: "panel",
    color: "--chart-9",
    hint: {
      label: "ATR · amplitude média",
      description: "Quanto o preço anda por dia, em reais",
      definition:
        "A média dos últimos 14 pregões da amplitude do dia: a distância entre a máxima e a mínima, contando o salto desde o fechamento anterior.",
      example: "Ex.: ATR de R$ 0,64 numa ação de R$ 32 quer dizer que ela anda uns 2% por dia.",
      reading:
        "Mede o tamanho do movimento, não a direção: não aponta compra nem venda. ATR alto é preço agitado, e uma ordem de stop precisa de mais folga.",
      format: text,
    },
    summary: (params) => String(params.atr_period),
  },
  {
    key: "obv",
    name: "OBV",
    description: "Soma o volume dos dias de alta e tira o dos de baixa",
    place: "panel",
    color: "--chart-8",
    hint: {
      label: "OBV · saldo de volume",
      description: "Volume dos dias de alta menos o dos dias de baixa",
      definition:
        "Começa em zero e, a cada pregão, soma o volume se o preço subiu e tira se caiu. O número em si importa pouco: o que conta é a direção.",
      example:
        "Ex.: +207,2 mi em 5 dias quer dizer que os dias de alta tiveram 207 milhões de ações a mais que os de baixa.",
      reading: "Subindo nos últimos 5 dias, há mais volume nas altas (compra); caindo, mais nas baixas (venda).",
      format: text,
    },
    summary: null,
  },
];

export const INDICATOR_BY_KEY = Object.fromEntries(INDICATORS.map((info) => [info.key, info])) as Record<
  IndicatorKey,
  IndicatorInfo
>;

/** Os padrões de mercado, os mesmos do servidor. */
export const DEFAULT_PARAMS: IndicatorParams = {
  averages: [
    { kind: "sma", period: 20 },
    { kind: "ema", period: 50 },
  ],
  bollinger_period: 20,
  bollinger_deviations: 2,
  rsi_period: 14,
  rsi_overbought: 70,
  rsi_oversold: 30,
  macd_fast: 12,
  macd_slow: 26,
  macd_signal: 9,
  stochastic_k: 14,
  stochastic_d: 3,
  atr_period: 14,
};

/** Os painéis embaixo do gráfico, na ordem em que aparecem. */
export const PANEL_KEYS = INDICATORS.filter((info) => info.place === "panel").map((info) => info.key);

/** Cor de cada média, pela posição dela na lista do seletor. */
export const AVERAGE_COLORS = ["--chart-5", "--chart-4", "--chart-3", "--chart-10"] as const;

export const MAX_AVERAGES = AVERAGE_COLORS.length;

/** Limites de cada parâmetro, os mesmos que o servidor aceita. */
export const PARAM_LIMITS = {
  average: { min: 2, max: 200 },
  bollinger_period: { min: 2, max: 100 },
  bollinger_deviations: { min: 0.5, max: 5 },
  rsi_period: { min: 2, max: 50 },
  rsi_overbought: { min: 50, max: 95 },
  rsi_oversold: { min: 5, max: 50 },
  macd_fast: { min: 2, max: 50 },
  macd_slow: { min: 3, max: 100 },
  macd_signal: { min: 2, max: 50 },
  stochastic_k: { min: 2, max: 50 },
  stochastic_d: { min: 1, max: 20 },
  atr_period: { min: 2, max: 50 },
} as const;

export function averageLabel(average: MovingAverage) {
  return `${average.kind === "sma" ? "MMS" : "MME"} ${average.period}`;
}

/** Quantos itens o gráfico mostra: cada média conta, e cada painel também. */
export function countShown(settings: IndicatorSettings) {
  return settings.visible.reduce((total, key) => total + (key === "averages" ? settings.params.averages.length : 1), 0);
}

export function isShown(settings: IndicatorSettings, key: IndicatorKey) {
  return settings.visible.includes(key);
}

export function toggled(settings: IndicatorSettings, key: IndicatorKey, on: boolean): IndicatorSettings {
  const visible = settings.visible.filter((k) => k !== key);
  return { ...settings, visible: on ? [...visible, key] : visible };
}

export function withParams(settings: IndicatorSettings, params: Partial<IndicatorParams>): IndicatorSettings {
  return { ...settings, params: { ...settings.params, ...params } };
}

export const VERDICT_LABELS: Record<NonNullable<TechnicalSummary["verdict"]>, string> = {
  strong_buy: "Compra forte",
  buy: "Compra",
  neutral: "Neutro",
  sell: "Venda",
  strong_sell: "Venda forte",
};

export const SIGNAL_LABELS: Record<TechnicalReading["signal"], string> = {
  buy: "Compra",
  neutral: "Neutro",
  sell: "Venda",
  none: "Sem lado",
};

const READING_NAMES = {
  bollinger: "Bollinger",
  rsi: "IFR",
  macd: "MACD",
  stochastic: "Estocástico",
  atr: "ATR",
  obv: "OBV",
} as const;

/** O nome curto da leitura no resumo; as médias levam o período, que distingue uma da outra. */
export function readingName(reading: TechnicalReading) {
  return reading.key === "sma" || reading.key === "ema" ? reading.label : READING_NAMES[reading.key];
}

/** O valor do dia de cada leitura, na unidade dela. */
export function displayReading(reading: TechnicalReading) {
  if (reading.value === null) return "—";
  switch (reading.key) {
    case "sma":
    case "ema":
      return displayMoney(reading.value);
    case "bollinger":
      return `${displayNumber(reading.lower ?? 0, 1)} a ${displayNumber(reading.upper ?? 0, 1)}`;
    case "rsi":
    case "stochastic":
      return displayNumber(reading.value, 1);
    case "macd":
      return displayNumber(reading.value);
    case "atr":
      return `${displayMoney(reading.value)}/dia`;
    case "obv":
      return displaySignedCompact(reading.value);
  }
}

export function displaySignedCompact(value: number) {
  return `${value > 0 ? "+" : value < 0 ? "−" : ""}${displayCompactNumber(Math.abs(value))}`;
}

/** A regra fixa que dá a leitura de cada indicador, com os níveis escolhidos. */
export function readingRule(reading: TechnicalReading, params: IndicatorParams) {
  switch (reading.key) {
    case "sma":
    case "ema":
      return "Preço acima da média lê-se compra; abaixo, venda.";
    case "bollinger":
      return "Fechar acima da banda de cima lê-se venda; abaixo da de baixo, compra; dentro da faixa, neutro.";
    case "rsi":
      return `Acima de ${params.rsi_overbought} lê-se venda (subiu rápido demais); abaixo de ${params.rsi_oversold}, compra (caiu rápido demais); entre os dois, neutro.`;
    case "macd":
      return "Linha acima do sinal lê-se compra; abaixo, venda.";
    case "stochastic":
      return "Acima de 80 lê-se venda; abaixo de 20, compra; no meio, neutro.";
    case "atr":
      return "Mede o tamanho do movimento, não a direção: fica fora da conta.";
    case "obv":
      return "Saldo subindo nos últimos 5 pregões lê-se compra; caindo, venda.";
  }
}

/** As faixas da régua dos indicadores de escala fixa (0 a 100); os demais não têm régua. */
export function scaleBands(key: IndicatorKey, params: IndicatorParams) {
  switch (key) {
    case "rsi":
      return { low: params.rsi_oversold, high: params.rsi_overbought };
    case "stochastic":
      return { low: 20, high: 80 };
    default:
      return null;
  }
}

/** A dica de cada leitura do resumo é a do indicador que ela lê. */
export const READING_HINT: Record<TechnicalReading["key"], MetricInfo> = {
  sma: INDICATOR_BY_KEY.averages.hint,
  ema: INDICATOR_BY_KEY.averages.hint,
  bollinger: INDICATOR_BY_KEY.bollinger.hint,
  rsi: INDICATOR_BY_KEY.rsi.hint,
  macd: INDICATOR_BY_KEY.macd.hint,
  stochastic: INDICATOR_BY_KEY.stochastic.hint,
  atr: INDICATOR_BY_KEY.atr.hint,
  obv: INDICATOR_BY_KEY.obv.hint,
};

export const SUMMARY_HINT: MetricInfo = {
  label: "Resumo técnico",
  description: "A leitura de cada indicador no dia e a soma delas",
  definition:
    "Cada indicador com lado vota compra, neutro ou venda por uma regra fixa, como no Investing.com. A nota é (compras − vendas) ÷ indicadores com valor. O ATR não tem lado e fica fora.",
  example: "Ex.: 4 compras − 1 venda = 3 de 7, 43%: Compra.",
  reading:
    "Compra forte a partir de 50%; Compra de 20% a 50%; Neutro entre −20% e 20%; Venda de −20% a −50%; Venda forte abaixo de −50%. É um retrato do dia, não uma previsão.",
  format: text,
};

/** O nome com artigo, para frases: as médias são femininas ("a MMS 20"), o resto masculino. */
export function readingWithArticle(reading: TechnicalReading) {
  return `${reading.key === "sma" || reading.key === "ema" ? "a" : "o"} ${readingName(reading)}`;
}

/**
 * A leitura que destrava o resumo: com os indicadores com lado em ordem de pregões
 * necessários, é a que completa a maioria.
 */
export function summaryUnlock(summary: TechnicalSummary) {
  const sided = summary.readings
    .filter((reading) => reading.key !== "atr")
    .sort((a, b) => a.needed_sessions - b.needed_sessions);
  return sided[Math.floor(summary.sided / 2)];
}
