import type { Profession } from "@/types";
import { professionIncome, TAG_NAMES, type TagKey } from "./professions";
import { displayDecimal, displayMoneyWhole } from "./utils/display";

/** Dica de uma etiqueta: o que ela é e uma tabela curta de como mexe na renda. */
export type TagTable = {
  title: string;
  subtitle: string;
  header: [string, string];
  rows: [string, string][];
  footnote: string;
};

// Constantes do backend (core/professions.py, features/economy/growth.py, core/life_events.py)
// Fator da renda = máx(1 + sensibilidade × (valor − neutro), piso), limitado ao teto quando há
type DriverCurve = { sensitivity: number; neutral: number; floor: number; ceiling?: number };
const DRIVER_CURVES = {
  gdp: { sensitivity: 3, neutral: 0.02, floor: 0.5 },
  dollar: { sensitivity: 1, neutral: 0, floor: 0.5, ceiling: 2 },
  selic: { sensitivity: 4, neutral: 0.12, floor: 0.5, ceiling: 2 },
  stocks: { sensitivity: 1.5, neutral: 0.12, floor: 0.4, ceiling: 2 },
} as const satisfies Record<string, DriverCurve>;
const CLT_GDP_SHARE = 0.5;
const NEUTRAL_UNEMPLOYMENT = 0.09;
// Imprevistos por ano na sala padrão, e a fração deles que é demissão (peso 1 de 40 no catálogo)
const UNEXPECTED_PER_YEAR = 3;
const LAYOFF_SHARE = 1 / 40;
const REFERENCE_WELFARE_SPENDING = 0.015;
const WELFARE_BENEFIT_MULTIPLE = 0.4;
const GIG_MULTIPLE = 0.5;
// O IPCA do ano usado nos exemplos de aumento
const EXAMPLE_INFLATION = 0.04;
const TAX_REFERENCE = { personalTax: 0.15, corporateTax: 0.34, consumptionTax: 0.18 } as const;

const TAX_SUBTITLES = {
  personalTax: "O imposto de renda que o governo cobra",
  corporateTax: "O imposto de renda que o governo cobra das empresas",
  consumptionTax: "O imposto que o governo cobra sobre o que se compra",
} as const;

/** Percentual inteiro ou com vírgula, com o menos tipográfico ("−15%"). */
function percent(fraction: number) {
  const text = `${displayDecimal(Math.round(fraction * 10000) / 100)}%`;
  return text.replace("-", "−");
}

function signedPercent(fraction: number) {
  const value = Math.round(fraction * 100);
  return value > 0 ? `+${value}%` : value < 0 ? `−${Math.abs(value)}%` : "";
}

/** "R$ 6.360 (+6%)": o valor e o quanto ele se afasta da renda de partida. */
function incomeAgainst(value: number, base: number, note?: string) {
  const delta = signedPercent(value / base - 1);
  const suffix = note ?? (delta ? delta : "");
  return suffix ? `${displayMoneyWhole(value)} (${suffix})` : displayMoneyWhole(value);
}

function driverFactor(curve: DriverCurve, value: number) {
  const factor = Math.max(1 + curve.sensitivity * (value - curve.neutral), curve.floor);
  return curve.ceiling === undefined ? factor : Math.min(factor, curve.ceiling);
}

type DriverTag = "dollar" | "selic" | "stocks";

const DRIVER_TABLES: Record<
  DriverTag,
  { subtitle: string; header: [string, string]; samples: [number, string][]; footnote: string }
> = {
  dollar: {
    subtitle: "A variação do dólar nos últimos 12 meses",
    header: ["Dólar em 12 meses", "Sua renda"],
    samples: [
      [1, "+100% ou mais"],
      [0.2, "+20%"],
      [0, "0%"],
      [-0.2, "−20%"],
      [-0.5, "−50% ou menos"],
    ],
    footnote: "Cada ponto de variação do dólar move 1% da renda, entre a metade e o dobro dela.",
  },
  selic: {
    subtitle: "A taxa básica de juros ao ano",
    header: ["SELIC ao ano", "Sua renda"],
    samples: [
      [0.2, "20%"],
      [0.16, "16%"],
      [0.12, "12%"],
      [0.08, "8%"],
      [0.04, "4%"],
    ],
    footnote: "Cada ponto da SELIC longe de 12% move 4% da renda.",
  },
  stocks: {
    subtitle: "Quanto o Ibovespa rendeu nos últimos 12 meses",
    header: ["Ibovespa em 12 meses", "Sua renda"],
    samples: [
      [0.4, "+40%"],
      [0.12, "+12%"],
      [0, "0%"],
      [-0.2, "−20%"],
      [-0.4, "−40% ou menos"],
    ],
    footnote: "Cada ponto longe de 12% move 1,5% da renda, entre 40% e o dobro dela.",
  },
};

function driverTable(tag: DriverTag, base: number): TagTable {
  const curve: DriverCurve = DRIVER_CURVES[tag];
  const { subtitle, header, samples, footnote } = DRIVER_TABLES[tag];
  return {
    title: TAG_NAMES[tag],
    subtitle,
    header,
    rows: samples.map(([value, label]): [string, string] => {
      const factor = driverFactor(curve, value);
      const note = factor === curve.floor ? "piso" : factor === curve.ceiling ? "teto" : undefined;
      return [label, value === curve.neutral ? displayMoneyWhole(base) : incomeAgainst(base * factor, base, note)];
    }),
    footnote,
  };
}

function gdpTable(profession: Profession, base: number): TagTable {
  const title = TAG_NAMES.gdp;
  const subtitle = "O crescimento da economia nos últimos 12 meses";
  if (profession === "ENTREPRENEUR") {
    const income = (growth: number) => base * driverFactor(DRIVER_CURVES.gdp, growth);
    return {
      title,
      subtitle,
      header: ["PIB de 12 meses", "Sua renda"],
      rows: [
        ["4%", incomeAgainst(income(0.04), base)],
        ["2%", displayMoneyWhole(income(0.02))],
        ["0%", incomeAgainst(income(0), base)],
        ["−15% ou menos", incomeAgainst(income(-0.15), base, "piso")],
      ],
      footnote: "Cada ponto longe de 2% move 3% da renda.",
    };
  }
  // CLT: o reajuste real é metade do PIB, nunca negativo, e soma ao IPCA uma vez por ano
  const income = (growth: number) => base * (1 + EXAMPLE_INFLATION + CLT_GDP_SHARE * Math.max(growth, 0));
  return {
    title,
    subtitle,
    header: ["PIB de 12 meses", "Renda após o aniversário"],
    rows: [
      ["4%", displayMoneyWhole(income(0.04))],
      ["2%", displayMoneyWhole(income(0.02))],
      ["0% ou menos", incomeAgainst(income(0), base, "só o IPCA")],
    ],
    footnote: "Com IPCA de 4% no ano. O aumento acima da inflação é metade do PIB e sobe uma vez por ano.",
  };
}

function unemploymentTable(): TagTable {
  // Demissões por ano = imprevistos por ano × fração de demissão × (desemprego ÷ desemprego neutro)
  const years = (unemployment: number) =>
    Math.round(1 / (UNEXPECTED_PER_YEAR * LAYOFF_SHARE * (unemployment / NEUTRAL_UNEMPLOYMENT)));
  return {
    title: TAG_NAMES.unemployment,
    subtitle: "A fatia de quem procura emprego e não acha",
    header: ["Desemprego", "Sorteio de demissão"],
    rows: [0.045, 0.09, 0.18].map((unemployment): [string, string] => [
      percent(unemployment),
      `1 vez a cada ${years(unemployment)} anos`,
    ]),
    footnote: "Em média, com os imprevistos da sala no padrão. Cada sorteio é um mês sem essa renda.",
  };
}

function taxTable(tag: keyof typeof TAX_REFERENCE, base: number): TagTable {
  const reference = TAX_REFERENCE[tag];
  // O que a alíquota passa da lei, em pontos, sai da renda
  const income = (rate: number) => base * (1 - (rate - reference));
  const rates = [reference - 0.05, reference, reference + 0.05];
  return {
    title: TAG_NAMES[tag],
    subtitle: TAX_SUBTITLES[tag],
    header: ["Alíquota", "Sua renda"],
    rows: rates.map((rate): [string, string] =>
      rate === reference
        ? [`${percent(rate)}, a da lei`, displayMoneyWhole(base)]
        : [percent(rate), incomeAgainst(income(rate), base)],
    ),
    footnote: "O que a alíquota passa da lei sai da renda.",
  };
}

function welfareSpendingTable(salary: number): TagTable {
  const benefit = (spending: number) => salary * WELFARE_BENEFIT_MULTIPLE * (spending / REFERENCE_WELFARE_SPENDING);
  return {
    title: TAG_NAMES.welfareSpending,
    subtitle: "Quanto do PIB o governo gasta com auxílio por ano",
    header: ["Gasto", "Seu auxílio"],
    rows: [0.0075, 0.015, 0.03].map((spending): [string, string] => [
      `${percent(spending)} do PIB`,
      displayMoneyWhole(benefit(spending)),
    ]),
    footnote: `O bico, ${displayMoneyWhole(salary * GIG_MULTIPLE)}, não muda.`,
  };
}

function raiseTable(tag: "servantRaise" | "retireeRaise", base: number): TagTable {
  const income = (raise: number) => base * (1 + EXAMPLE_INFLATION + raise);
  return {
    title: TAG_NAMES[tag],
    subtitle: "O reajuste acima da inflação que o governo aprova",
    header: ["Aumento", "Renda após o aniversário"],
    rows: [
      ["0%", `${displayMoneyWhole(income(0))} (só o IPCA)`],
      ["2%", displayMoneyWhole(income(0.02))],
      ["5%", displayMoneyWhole(income(0.05))],
    ],
    footnote: "Com IPCA de 4% no ano. Sobe uma vez por ano.",
  };
}

/** A tabela da dica de uma etiqueta, calculada com as regras reais sobre a renda da profissão. */
export function tagTable(tag: TagKey, profession: Profession, salary: number): TagTable {
  const base = professionIncome(profession, salary);
  switch (tag) {
    case "gdp":
      return gdpTable(profession, base);
    case "dollar":
    case "selic":
    case "stocks":
      return driverTable(tag, base);
    case "unemployment":
      return unemploymentTable();
    case "personalTax":
    case "corporateTax":
    case "consumptionTax":
      return taxTable(tag, base);
    case "welfareSpending":
      return welfareSpendingTable(salary);
    case "servantRaise":
    case "retireeRaise":
      return raiseTable(tag, base);
  }
}
