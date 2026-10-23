import type { StrategyInfo, StrategyParam, StrategyParamValue } from "@/types";

export type ParamValues = Record<string, StrategyParamValue>;
/** O que o jogador digitou: texto nos campos numéricos, lista nas ações. */
export type ParamDraft = Record<string, string | string[]>;

export function defaultValues(strategy: StrategyInfo): ParamValues {
  return Object.fromEntries(strategy.params.map((param) => [param.key, param.default]));
}

export function toDraft(values: ParamValues): ParamDraft {
  return Object.fromEntries(
    Object.entries(values).map(([key, value]) => [key, typeof value === "number" ? String(value) : value]),
  );
}

/** Valores prontos para o servidor; nulo enquanto algum campo numérico não é um inteiro. */
export function fromDraft(params: StrategyParam[], draft: ParamDraft): ParamValues | null {
  const values: ParamValues = {};
  for (const param of params) {
    const entry = draft[param.key];
    if (param.kind === "tickers") {
      values[param.key] = Array.isArray(entry) ? entry : [];
      continue;
    }
    if (typeof entry !== "string" || !/^\d+$/.test(entry.trim())) return null;
    values[param.key] = Number(entry);
  }
  return values;
}

export function sameValues(a: ParamValues, b: ParamValues) {
  const keys = Object.keys(a);
  return (
    keys.length === Object.keys(b).length &&
    keys.every((key) => {
      const left = a[key];
      const right = b[key];
      return Array.isArray(left) && Array.isArray(right)
        ? left.length === right.length && left.every((ticker, index) => ticker === right[index])
        : left === right;
    })
  );
}

/** Texto de apoio sob o campo: o padrão e a faixa que vale ("Padrão 50 · de 5 a 100"). */
export function rangeHint(param: StrategyParam) {
  if (param.kind === "tickers") return null;
  const unit = param.unit === "%" ? "%" : "";
  return `Padrão ${String(param.default)}${unit} · de ${String(param.min)}${unit} a ${String(param.max)}${unit}`;
}
