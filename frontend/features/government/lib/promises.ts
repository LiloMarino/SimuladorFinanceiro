import type { MetricInfo } from "@/shared/lib/metric-info";
import { isSpending } from "@/shared/lib/spending-kinds";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import type {
  CampaignPromise,
  MeasureKind,
  PromiseRequest,
  PromiseState,
  PromisesPanel,
  PromisesPreview,
  VoterGroup,
  VoterGroupInfo,
} from "@/types";

import { percentLabel } from "./government";
import { spendingValue } from "./spending";

const MINUS = "−";

export type PromiseOption = PromisesPanel["options"][number];
export type PromiseRow = PromisesPreview["items"][number]["rows"][number];

/** O rascunho de uma promessa na lista da chapa: o que o servidor recebe. */
export type PromiseDraft = {
  kind: MeasureKind;
  target: string | null;
  sector: string | null;
  segment: string | null;
};

export const PROMISE_STATE: Record<
  PromiseState,
  { label: string; variant: "success" | "info" | "secondary" | "destructive" }
> = {
  FULFILLED: { label: "Cumprida", variant: "success" },
  IN_PROGRESS: { label: "Em andamento", variant: "info" },
  UNTOUCHED: { label: "Sem andar", variant: "secondary" },
  CONTRARY: { label: "Na direção contrária", variant: "destructive" },
};

/** O estado com a fração do caminho andado: "Em andamento · 50%", "Na direção contrária · −50%". */
export function stateLabel(state: PromiseState, done: string | number) {
  const base = PROMISE_STATE[state].label;
  const percent = Math.round(Number(done) * 100);
  if (state === "IN_PROGRESS") return `${base} · ${percent}%`;
  if (state === "CONTRARY") return `${base} · ${MINUS}${Math.abs(percent)}%`;
  return base;
}

/** Quantas promessas estão em cada estado, para o resumo do cartão. */
export function stateSummary(items: { state: PromiseState }[]) {
  const count = (state: PromiseState) => items.filter((item) => item.state === state).length;
  const fulfilled = count("FULFILLED");
  const progress = count("IN_PROGRESS");
  const untouched = count("UNTOUCHED");
  const contrary = count("CONTRARY");
  const parts: string[] = [];
  if (fulfilled) parts.push(`${fulfilled} ${fulfilled === 1 ? "cumprida" : "cumpridas"}`);
  if (progress) parts.push(`${progress} em andamento`);
  if (untouched) parts.push(`${untouched} sem andar`);
  if (contrary) parts.push(`${contrary} na direção contrária`);
  return parts.join(" · ");
}

/** Número com uma casa e sinal: 1.2 → "+1,2", -0.4 → "−0,4"; zero vira "0". */
export function signedDecimal(value: string | number) {
  const number = Number(value);
  if (Math.abs(number) < 0.05) return "0";
  const text = Math.abs(number).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  return `${number > 0 ? "+" : MINUS}${text}`;
}

/** O valor de uma medida como a tela escreve: a alíquota em %, o teto da isenção em reais por mês. */
export function promiseValue(kind: MeasureKind, value: string | number) {
  if (isSpending(kind)) return spendingValue(kind, value);
  return kind === "STOCK_EXEMPTION" ? `até ${displayMoneyCompact(value)}/mês` : percentLabel(value);
}

/** A mesma medida: o tipo mais o setor e o segmento, como o servidor distingue as promessas. */
export const promiseKey = (promise: Pick<PromiseDraft, "kind" | "sector" | "segment">) =>
  `${promise.kind}|${promise.sector ?? ""}|${promise.segment ?? ""}`;

/** O pedido de uma promessa; a de setor é sim ou não e não leva alvo. */
export function toRequest(draft: PromiseDraft): PromiseRequest {
  return draft.sector === null
    ? { kind: draft.kind, target: draft.target }
    : { kind: draft.kind, sector: draft.sector, segment: draft.segment };
}

/** O rascunho que já é uma promessa válida: o setor escolhido, ou um alvo diferente do que vale hoje. */
export function isComplete(draft: PromiseDraft, options: PromiseOption[]) {
  if (draft.sector !== null) return true;
  const option = options.find((candidate) => candidate.kind === draft.kind);
  return draft.target !== null && option !== undefined && Number(draft.target) !== Number(option.baseline);
}

export function draftOf(promise: CampaignPromise): PromiseDraft {
  return { kind: promise.kind, target: promise.target, sector: promise.sector, segment: promise.segment };
}

/** O efeito de uma promessa no eleitorado todo: o apoio que rende em cada grupo, pesado pelo tamanho dele. */
export function weightedSupport(rows: PromiseRow[], groups: Pick<VoterGroupInfo, "group" | "weight">[]) {
  const weights = new Map<VoterGroup, number>(groups.map((info) => [info.group, Number(info.weight)]));
  return rows.reduce((sum, row) => sum + Number(row.support) * (weights.get(row.group) ?? 0), 0);
}

export const PROMISE_YIELD: MetricInfo = {
  label: "Rende agora, em apoio",
  description: "O apoio que a promessa soma ao partido desde o anúncio",
  definition:
    "Cada grupo que quer a medida soma apoio ao partido pela promessa, e quem não quer tira. O ganho é multiplicado por (1 − rejeição ÷ 100): quem já rejeita o partido acredita menos na promessa. Não cai com o tempo.",
  example:
    "Ex.: a promessa renderia 6 pontos entre os investidores, mas a rejeição deles ao partido é 9: rende 6 × 0,91 = 5,5.",
  reading:
    "Positivo ajuda o partido no grupo; negativo atrapalha. Quem não quer a medida tira cheio, sem desconto pela rejeição.",
  format: (value) => signedDecimal(value),
};

export const PROMISE_BREACH: MetricInfo = {
  label: "Se descumprir",
  description: "A rejeição que soma no grupo se a promessa não sair",
  definition:
    "No fim do mandato, cada promessa que o país não andou soma rejeição entre quem queria a medida. Se o país andou na direção contrária, a rejeição sai 1,5 vez maior. A rejeição só cai com reparação.",
  example: "Ex.: +6 de rejeição entre os investidores: o saldo do partido com eles cai 6 pontos.",
  reading: "Cumprida, a promessa soma afinidade e repara rejeição no mesmo grupo. Zero é o melhor.",
  format: (value) => signedDecimal(value),
};
