import { format } from "date-fns";
import { displayNumber } from "@/shared/lib/utils/display";
import type { MarketRegime } from "@/types";

export const FUTURE_DOCS_URL =
  "https://lilomarino.github.io/SimuladorFinanceiro/como-usar/futuro-gerado";

export const TEMPERATURE = { min: 0, max: 3, step: 0.1, default: 1 } as const;
export const INFLATION_SHOCK = {
  min: -5,
  max: 20,
  step: 1,
  default: 0,
} as const;

const MINUS = "−";

/** Número com o sinal de menos tipográfico, como as telas de números mostram. */
export const withMinus = (text: string) => text.replace("-", MINUS);

/** Opção de "Começar em": o clima de hoje ou um clima fixo para o primeiro trimestre. */
export type StartChoice = "TODAY" | MarketRegime;

export const START_CHOICES: {
  value: Exclude<StartChoice, "TODAY">;
  label: string;
}[] = [
  { value: "CALM", label: "Calmaria" },
  { value: "NORMAL", label: "Normal" },
  { value: "AGITATED", label: "Crise" },
];

/** O clima como a pessoa lê: o Ibovespa agitado é "crise". */
export const REGIME_NAMES: Record<MarketRegime, string> = {
  CALM: "calmaria",
  NORMAL: "normal",
  AGITATED: "crise",
};

/** Volatilidade do 1º ano medida começando em cada clima. */
export const FIRST_YEAR_VOLATILITY: Record<MarketRegime, number> = {
  CALM: 18,
  NORMAL: 22,
  AGITATED: 30,
};

export const startChoiceToRegime = (
  choice: StartChoice,
): MarketRegime | null => (choice === "TODAY" ? null : choice);
export const regimeToStartChoice = (
  regime: MarketRegime | null | undefined,
): StartChoice => regime ?? "TODAY";

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

const TEMPERATURE_LEVELS: TemperatureLevel[] = [
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
  const level = Math.min(
    Math.max(Math.round(temperature), TEMPERATURE.min),
    TEMPERATURE.max,
  );
  return TEMPERATURE_LEVELS[level];
}

export const TEMPERATURE_TABLE = TEMPERATURE_LEVELS.map(
  ({ level, volatility, crashYears }) => ({
    level,
    volatility,
    crashYears,
  }),
);

export const TEMPERATURE_MARKS = [
  { value: 0, label: "0 calmo" },
  { value: 1, label: "1 histórico" },
  { value: 2, label: "2 ≈ 2008" },
  { value: 3, label: "3" },
];

export const displayTemperature = (temperature: number) =>
  displayNumber(temperature, 1);

// Medianas de 50 futuros partindo de hoje, para cada marca do choque
export const INFLATION_SHOCK_TABLE = [
  { shock: -5, inflationPeak: 6, selicPeak: 13, twoYearDrop: -30 },
  { shock: 0, inflationPeak: 7, selicPeak: 15, twoYearDrop: -26 },
  { shock: 10, inflationPeak: 14, selicPeak: 28, twoYearDrop: -36 },
  { shock: 20, inflationPeak: 22, selicPeak: 43, twoYearDrop: -57 },
] as const;

export const signedShock = (shock: number) =>
  shock > 0 ? `+${shock}` : shock < 0 ? `${MINUS}${Math.abs(shock)}` : "0";

export const INFLATION_SHOCK_MARKS = INFLATION_SHOCK_TABLE.map(({ shock }) => ({
  value: shock,
  label: signedShock(shock),
}));

/** Para um valor entre as marcas vale a leitura da marca mais próxima. */
export function inflationShockReading(shock: number) {
  return INFLATION_SHOCK_TABLE.reduce((nearest, row) =>
    Math.abs(row.shock - shock) < Math.abs(nearest.shock - shock)
      ? row
      : nearest,
  );
}

/** "0 pontos", "+10 pontos", "+1 ponto". */
export const displayShock = (shock: number) =>
  `${signedShock(shock)} ${Math.abs(shock) === 1 ? "ponto" : "pontos"}`;

/** 31/12 do ano que fica `years` anos à frente: o atalho "+N anos" do campo de data. */
export const endOfYearAhead = (years: number) =>
  format(new Date(new Date().getFullYear() + years, 11, 31), "yyyy-MM-dd");

/** Semente sorteada: inteiro de até 9 dígitos, curto o bastante para digitar e anotar. */
export const drawSeed = () => String(Math.floor(Math.random() * 10 ** 9));
