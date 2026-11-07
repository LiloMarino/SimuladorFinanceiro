import { format } from "date-fns";
import { displayNumber } from "@/shared/lib/utils/display";

export const FUTURE_DOCS_URL = "https://lilomarino.github.io/SimuladorFinanceiro/como-usar/futuro-gerado";

export const TEMPERATURE = { min: 0, max: 3, step: 0.1, default: 1 } as const;
export const INFLATION_LEVEL = { min: -5, max: 20, step: 1, default: 0 } as const;
export const SURGE_FREQUENCY = { min: 0, max: 5, step: 0.5, default: 0 } as const;
export const SURGE_INTENSITY = { min: 2, max: 20, step: 1, default: 6 } as const;

const MINUS = "−";

/** Número com o sinal de menos tipográfico, como as telas de números mostram. */
export const withMinus = (text: string) => text.replace("-", MINUS);

// Medido em 100 futuros de 5 anos para cada temperatura inteira
type TemperatureLevel = {
  level: number;
  headline: string;
  subject: string;
  volatility: number;
  crashYears: number;
  closing: string;
  extreme?: boolean;
};

const TEMPERATURE_LEVELS: [TemperatureLevel, TemperatureLevel, TemperatureLevel, TemperatureLevel] = [
  {
    level: 0,
    headline: "O mais calmo possível.",
    subject: "Um ano típico do Ibovespa oscila uns",
    volatility: 17,
    crashYears: 5,
    closing: "anos a bolsa cai mais de 30% em algum momento.",
  },
  {
    level: 1,
    headline: "O histórico como foi.",
    subject: "Um ano típico do Ibovespa oscila uns",
    volatility: 24,
    crashYears: 28,
    closing: "anos a bolsa cai mais de 30% em algum momento.",
  },
  {
    level: 2,
    headline: "Perto de 2008 o tempo todo.",
    subject: "Um ano típico oscila uns",
    volatility: 43,
    crashYears: 64,
    closing: "anos a bolsa cai mais de 30%.",
  },
  {
    level: 3,
    headline: "Modo apocalipse:",
    subject: "todo ano é pior que 2008. Um ano típico oscila uns",
    volatility: 68,
    crashYears: 96,
    closing: "anos a bolsa cai mais de 30%.",
    extreme: true,
  },
];

/** A leitura mostrada é a do nível inteiro mais próximo. */
export function temperatureReading(temperature: number): TemperatureLevel {
  const level = Math.min(Math.max(Math.round(temperature), TEMPERATURE.min), TEMPERATURE.max);
  return TEMPERATURE_LEVELS[level] ?? TEMPERATURE_LEVELS[0];
}

export const TEMPERATURE_TABLE = TEMPERATURE_LEVELS.map(({ level, volatility, crashYears }) => ({
  level,
  volatility,
  crashYears,
}));

export const TEMPERATURE_MARKS = [
  { value: 0, label: "0 calmo" },
  { value: 1, label: "1 histórico" },
  { value: 2, label: "2 ≈ 2008" },
  { value: 3, label: "3" },
];

export const displayTemperature = (temperature: number) => displayNumber(temperature, 1);

// Medianas de 50 futuros de 10 anos partindo de hoje, para cada marca do nível; a bolsa é a
// variação do Ibovespa em 10 anos já descontada a inflação
export const INFLATION_LEVEL_TABLE = [
  { level: -5, inflation: 1, selic: 9, stocksReal: 35 },
  { level: 0, inflation: 6, selic: 14, stocksReal: 21 },
  { level: 10, inflation: 16, selic: 24, stocksReal: -4 },
  { level: 20, inflation: 26, selic: 35, stocksReal: -23 },
] as const;

// Médias de 50 futuros de 10 anos com surtos de 6 pontos: em quantos anos a inflação
// de 12 meses passa de 10%
export const SURGE_FREQUENCY_TABLE = [
  { frequency: 0, hotYears: 0.8 },
  { frequency: 1, hotYears: 1.9 },
  { frequency: 3, hotYears: 3.1 },
  { frequency: 5, hotYears: 4.9 },
] as const;

export const signedLevel = (level: number) =>
  level > 0 ? `+${level}` : level < 0 ? `${MINUS}${Math.abs(level)}` : "0";

export const INFLATION_LEVEL_MARKS = INFLATION_LEVEL_TABLE.map(({ level }) => ({
  value: level,
  label: signedLevel(level),
}));

export const SURGE_FREQUENCY_MARKS = SURGE_FREQUENCY_TABLE.map(({ frequency }) => ({
  value: frequency,
  label: String(frequency),
}));

export const SURGE_INTENSITY_MARKS = [2, 6, 12, 20].map((value) => ({ value, label: String(value) }));

/** Para um valor entre as marcas vale a leitura da marca mais próxima. */
function nearestRow<T>(rows: readonly T[], value: number, valueOf: (row: T) => number): T {
  return rows.reduce((nearest, row) =>
    Math.abs(valueOf(row) - value) < Math.abs(valueOf(nearest) - value) ? row : nearest,
  );
}

export const inflationLevelReading = (level: number) => nearestRow(INFLATION_LEVEL_TABLE, level, (row) => row.level);
export const surgeFrequencyReading = (frequency: number) =>
  nearestRow(SURGE_FREQUENCY_TABLE, frequency, (row) => row.frequency);

/** "0 pontos", "+10 pontos", "+1 ponto". */
export const displayLevel = (level: number) => `${signedLevel(level)} ${Math.abs(level) === 1 ? "ponto" : "pontos"}`;

/** "6 pontos", "1 ponto". */
export const displayIntensity = (points: number) => `${points} ${points === 1 ? "ponto" : "pontos"}`;

/** "0 surtos por década", "1 surto por década", "2,5 surtos por década". */
export const displaySurgeFrequency = (frequency: number) =>
  `${displayNumber(frequency, frequency % 1 === 0 ? 0 : 1)} ${frequency === 1 ? "surto" : "surtos"} por década`;

/** 31/12 do ano que fica `years` anos à frente: o atalho "+N anos" do campo de data. */
export const endOfYearAhead = (years: number) =>
  format(new Date(new Date().getFullYear() + years, 11, 31), "yyyy-MM-dd");

/** Quantos anos depois do último dado real o gerador aceita: o mesmo limite do servidor. */
const MAX_FUTURE_YEARS = 30;

/** Os 31/12 que o seletor "Até quando" oferece, do primeiro depois do último dado real até o limite. */
export const futureEndDates = (lastRealIso: string): string[] => {
  const lastYear = Number(lastRealIso.slice(0, 4));
  const first = `${lastYear}-12-31` > lastRealIso ? lastYear : lastYear + 1;
  return Array.from({ length: lastYear + MAX_FUTURE_YEARS - first + 1 }, (_, index) => `${first + index}-12-31`);
};

/** Semente sorteada: inteiro de até 9 dígitos, curto o bastante para digitar e anotar. */
export const drawSeed = () => String(Math.floor(Math.random() * 10 ** 9));
