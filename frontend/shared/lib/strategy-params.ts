import type { StrategyInfo, StrategyParam, StrategyParamValue } from "@/types";

export type ParamValues = Record<string, StrategyParamValue>;
/** O que o jogador digitou: texto nos campos numéricos e no ativo, lista nas ações. */
export type ParamDraft = Record<string, string | string[]>;

export function defaultValues(strategy: StrategyInfo): ParamValues {
  return Object.fromEntries(strategy.params.map((param) => [param.key, param.default]));
}

export function toDraft(values: ParamValues): ParamDraft {
  return Object.fromEntries(
    Object.entries(values).map(([key, value]) => [key, typeof value === "number" ? String(value) : value]),
  );
}

/** Valores prontos para o servidor; nulo enquanto algum campo numérico não é um inteiro ou falta o ativo. */
export function fromDraft(params: StrategyParam[], draft: ParamDraft): ParamValues | null {
  const values: ParamValues = {};
  for (const param of params) {
    const entry = draft[param.key];
    if (param.kind === "tickers") {
      values[param.key] = Array.isArray(entry) ? entry : [];
      continue;
    }
    if (param.kind === "ticker") {
      if (typeof entry !== "string" || entry === "") return null;
      values[param.key] = entry;
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
  if (param.kind === "ticker") return `Padrão ${String(param.default)}`;
  const unit = param.unit === "%" ? "%" : "";
  return `Padrão ${String(param.default)}${unit} · de ${String(param.min)}${unit} a ${String(param.max)}${unit}`;
}

/** O que a digitação ainda não permite, por campo: lista vazia, ativo faltando, não inteiro ou fora da faixa. */
export function draftErrors(params: StrategyParam[], draft: ParamDraft) {
  const errors: Record<string, string> = {};
  for (const param of params) {
    const entry = draft[param.key];
    if (param.kind === "tickers" && Array.isArray(entry) && entry.length === 0)
      errors[param.key] = "Escolha ao menos uma ação.";
    if (param.kind === "ticker" && entry === "") errors[param.key] = "Escolha uma ação.";
    if ((param.kind === "int" || param.kind === "percent") && typeof entry === "string") {
      if (!/^\d+$/.test(entry.trim())) errors[param.key] = "Digite um número inteiro.";
      else if (param.min != null && param.max != null && (Number(entry) < param.min || Number(entry) > param.max)) {
        const unit = param.unit === "%" ? "%" : "";
        errors[param.key] = `Use de ${param.min}${unit} a ${param.max}${unit}.`;
      }
    }
  }
  return errors;
}

export type ParamPill = {
  key: string;
  label: string;
  value: string;
  /** O valor difere do padrão da estratégia */
  changed: boolean;
};

const valueChanged = (value: StrategyParamValue | undefined, standard: StrategyParamValue) =>
  Array.isArray(value) && Array.isArray(standard)
    ? value.length !== standard.length || value.some((ticker, index) => ticker !== standard[index])
    : value !== standard;

/** Um resumo curto de cada parâmetro ("Média curta 20 dias"), marcando o que saiu do padrão. */
export function paramPills(strategy: StrategyInfo, values: ParamValues): ParamPill[] {
  return strategy.params.map((param) => {
    const value = values[param.key] ?? param.default;
    const text = Array.isArray(value)
      ? `${value.length} ${value.length === 1 ? "ação" : "ações"}`
      : typeof value === "number"
        ? `${value}${param.unit === "%" ? "%" : param.unit ? ` ${param.unit}` : ""}`
        : String(value);
    return { key: param.key, label: param.label, value: text, changed: valueChanged(value, param.default) };
  });
}
