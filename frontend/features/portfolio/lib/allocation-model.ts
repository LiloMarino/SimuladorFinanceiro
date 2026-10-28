import type { PortfolioState } from "@/types";

export type ClassKey = "variable" | "fixed" | "cash";

const CLASS_META: Record<ClassKey, { label: string; color: string }> = {
  variable: { label: "Renda variável", color: "var(--chart-1)" },
  fixed: { label: "Renda fixa", color: "var(--chart-2)" },
  cash: { label: "Caixa", color: "var(--input)" },
};

/** Quantos ativos a lista mostra antes de juntar o resto em "Outros". */
const ASSET_LIMIT = 8;

export type ClassSlice = {
  key: ClassKey;
  label: string;
  color: string;
  value: number;
  /** Parte do que o jogador tem (caixa + investido), de 0 a 1 */
  fraction: number;
};

export type AssetRow = {
  name: string;
  color: string;
  value: number;
  fraction: number;
  /** Quantos ativos o "Outros" reúne; ausente nos ativos individuais */
  count: number | undefined;
};

const fractionOf = (value: number, total: number) => (total > 0 ? value / total : 0);

/** As classes com dinheiro, na ordem renda variável, renda fixa e caixa. */
export function classSlices(portfolio: PortfolioState): ClassSlice[] {
  const total = Number(portfolio.assets_value);
  const values: Record<ClassKey, number> = {
    variable: Number(portfolio.variable_income_value),
    fixed: Number(portfolio.fixed_income_value),
    cash: Number(portfolio.cash),
  };
  return (Object.keys(CLASS_META) as ClassKey[])
    .filter((key) => values[key] > 0)
    .map((key) => ({
      key,
      ...CLASS_META[key],
      value: values[key],
      fraction: fractionOf(values[key], total),
    }));
}

/** Quantos ativos o jogador tem, de qualquer classe. */
export function assetCount(portfolio: PortfolioState) {
  return [...portfolio.variable_income, ...portfolio.fixed_income].filter((p) => Number(p.current_value) > 0).length;
}

/** Os maiores ativos de qualquer classe, do maior para o menor; o que passa do limite vira uma linha "Outros". */
export function topAssets(portfolio: PortfolioState, limit = ASSET_LIMIT): AssetRow[] {
  const total = Number(portfolio.assets_value);
  const assets = [
    ...portfolio.variable_income.map((p) => ({
      name: p.ticker,
      value: Number(p.current_value),
      color: CLASS_META.variable.color,
    })),
    ...portfolio.fixed_income.map((p) => ({
      name: p.asset.name,
      value: Number(p.current_value),
      color: CLASS_META.fixed.color,
    })),
  ]
    .filter((a) => a.value > 0)
    .sort((a, b) => b.value - a.value);

  const rows = assets
    .slice(0, limit)
    .map((a): AssetRow => ({ ...a, fraction: fractionOf(a.value, total), count: undefined }));
  const rest = assets.slice(limit);
  if (rest.length === 0) return rows;

  const restValue = rest.reduce((sum, a) => sum + a.value, 0);
  return [
    ...rows,
    {
      name: "Outros",
      color: "var(--faint-foreground)",
      value: restValue,
      fraction: fractionOf(restValue, total),
      count: rest.length,
    },
  ];
}

const point = (cx: number, cy: number, radius: number, angle: number) =>
  `${(cx + radius * Math.cos(angle)).toFixed(2)} ${(cy + radius * Math.sin(angle)).toFixed(2)}`;

/** Um setor do anel entre dois ângulos (radianos, a partir do topo, no sentido horário). */
export function ringArc(cx: number, cy: number, outer: number, inner: number, start: number, end: number) {
  const sweep = end - start;
  // Uma fatia que dá a volta inteira vira dois círculos concêntricos, preenchidos pela regra par-ímpar
  if (sweep >= 2 * Math.PI - 1e-6) {
    const circle = (r: number) =>
      `M${cx} ${cy - r} A${r} ${r} 0 1 1 ${cx} ${cy + r} A${r} ${r} 0 1 1 ${cx} ${cy - r} Z`;
    return `${circle(outer)} ${circle(inner)}`;
  }
  const large = sweep > Math.PI ? 1 : 0;
  return [
    `M${point(cx, cy, outer, start)}`,
    `A${outer} ${outer} 0 ${large} 1 ${point(cx, cy, outer, end)}`,
    `L${point(cx, cy, inner, end)}`,
    `A${inner} ${inner} 0 ${large} 0 ${point(cx, cy, inner, start)}`,
    "Z",
  ].join(" ");
}

/** Os ângulos de cada fatia, com uma folga entre vizinhas quando há mais de uma. */
export function sliceAngles(fractions: number[], gap = 0.03) {
  const total = fractions.reduce((sum, f) => sum + f, 0);
  const useGap = fractions.length > 1;
  let cursor = -Math.PI / 2;
  return fractions.map((fraction) => {
    const sweep = total > 0 ? (fraction / total) * 2 * Math.PI : 0;
    const start = cursor;
    cursor += sweep;
    const trim = useGap ? Math.min(gap / 2, sweep / 4) : 0;
    return { start: start + trim, end: cursor - trim };
  });
}
