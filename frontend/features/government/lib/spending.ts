import { isRaise, type SpendingKind } from "@/shared/lib/spending-kinds";
import type { GroupReaction, SpendingRow, VoterGroup } from "@/types";

const MINUS = "−";

const NUMBER = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
const SIGNED_NUMBER = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2, signDisplay: "exceptZero" });

/** Fração em pontos percentuais sem o símbolo: 0.0125 → "1,25". */
export function pointsOf(fraction: string | number) {
  return NUMBER.format(Math.round(Number(fraction) * 10000) / 100);
}

/** O mesmo com sinal e o menos tipográfico: −0.005 → "−0,5". */
export function signedPointsOf(fraction: string | number) {
  return SIGNED_NUMBER.format(Math.round(Number(fraction) * 10000) / 100).replace("-", MINUS);
}

/** O valor da medida como o jogo escreve: "1,4% do PIB" ou "ganho real de 2% ao ano". */
export function spendingValue(kind: SpendingKind, value: string | number) {
  return isRaise(kind) ? `ganho real de ${pointsOf(value)}% ao ano` : `${pointsOf(value)}% do PIB`;
}

/** A unidade que o campo de valor mostra ao lado do rótulo. */
export function spendingUnit(kind: SpendingKind) {
  return isRaise(kind) ? "em % ao ano, além da inflação" : "em % do PIB por ano";
}

type Window = { min: number; max: number };

/** A janela de uma medida: o passo para baixo (com piso em 0) e para cima (com o teto da medida). */
export function valueWindow(row: Pick<SpendingRow, "value" | "step" | "limit">): Window {
  const value = Number(row.value);
  const step = Number(row.step);
  return { min: Math.max(0, round(value - step)), max: Math.min(Number(row.limit), round(value + step)) };
}

/** "ponto" até 1 ponto ("0,5 ponto"), "pontos" acima. */
const pointUnit = (step: string | number) => (Number(step) <= 0.01 ? "ponto" : "pontos");

const round = (value: number) => Math.round(value * 10000) / 10000;

/** Os atalhos de passo do campo, em pontos: o auxílio e as obras andam em meios pontos, o reajuste em pontos inteiros. */
export function stepChips(kind: SpendingKind): number[] {
  return isRaise(kind) ? [-1, 1, 2, 3] : [-0.5, -0.25, 0.25, 0.5];
}

/** O texto do atalho: "+0,5", "−0,25". */
export const chipLabel = (points: number) => SIGNED_NUMBER.format(points).replace("-", MINUS);

/** O valor em % que o atalho põe no campo, a partir do valor de hoje. */
export function chipValueText(row: Pick<SpendingRow, "value">, points: number) {
  return NUMBER.format(round(Number(row.value) * 100 + points));
}

/** O atalho cai fora da janela quando passa do passo, do teto ou do piso. */
export function chipFits(row: Pick<SpendingRow, "value" | "step" | "limit">, points: number) {
  const target = round(Number(row.value) + points / 100);
  const { min, max } = valueWindow(row);
  return target >= min - 1e-9 && target <= max + 1e-9;
}

export type ValueCheck =
  | { status: "empty" }
  | { status: "same" }
  | { status: "outside"; window: Window }
  | { status: "ok"; fraction: string };

/** O que o texto digitado (em %) diz da medida: vazio, igual a hoje, fora da janela do passo ou pronto para enviar. */
export function checkValue(row: Pick<SpendingRow, "value" | "step" | "limit">, text: string): ValueCheck {
  const typed = Number(text.replace(",", "."));
  if (text.trim() === "" || !Number.isFinite(typed)) return { status: "empty" };
  const fraction = round(typed / 100);
  if (Math.abs(fraction - Number(row.value)) < 1e-9) return { status: "same" };
  const window = valueWindow(row);
  if (fraction < window.min - 1e-9 || fraction > window.max + 1e-9) return { status: "outside", window };
  return { status: "ok", fraction: String(fraction) };
}

/** "Hoje 1,4%. Numa medida, de 0,9% a 1,9%: até 0,5 ponto para cima ou para baixo." */
export function windowSentence(kind: SpendingKind, row: Pick<SpendingRow, "value" | "step" | "limit">) {
  const { min, max } = valueWindow(row);
  const step = pointsOf(row.step);
  const unit = pointUnit(row.step);
  const range = `de ${pointsOf(min)}% a ${pointsOf(max)}%`;
  if (isRaise(kind)) {
    return Number(row.value) === 0
      ? `Hoje 0%: a folha sobe só a inflação todo janeiro. Numa medida, até ${step} ${unit}: ${range} ao ano. Com ganho real, todo janeiro a folha sobe a inflação mais esse tanto.`
      : `Hoje ${pointsOf(row.value)}% de ganho real ao ano. Numa medida, ${range}: até ${step} ${unit} para cima ou para baixo, sem ficar abaixo de 0%.`;
  }
  return `Hoje ${pointsOf(row.value)}%. Numa medida, ${range}: até ${step} ${unit} para cima ou para baixo.`;
}

/** O aviso do número fora da janela, com o caminho para chegar mais longe. */
export function outsideSentence(kind: SpendingKind, row: Pick<SpendingRow, "value" | "step" | "limit">, text: string) {
  const { min, max } = valueWindow(row);
  const label = isRaise(kind) ? "o ganho real" : kind === "WELFARE_SPENDING" ? "o auxílio" : "as obras";
  const typed = Number(text.replace(",", ".")) / 100;
  const edge = typed > Number(row.value) ? max : min;
  return `Numa medida, ${label} muda até ${pointsOf(row.step)} ${pointUnit(row.step)}: de ${pointsOf(min)}% a ${pointsOf(max)}%. Para chegar a ${pointsOf(typed)}%, proponha ${pointsOf(edge)}% agora e outra medida depois que esta valer.`;
}

type ReasonText = { gain: string; loss: string };

/** O motivo direto de um grupo gostar ou não de uma medida de gasto, quando ele é quem recebe. */
const DIRECT_REASON: Partial<Record<SpendingKind, Partial<Record<VoterGroup, ReasonText>>>> = {
  WELFARE_SPENDING: {
    WELFARE: { gain: "recebem mais quando a medida vale", loss: "recebem menos quando a medida vale" },
  },
  SERVANT_RAISE: {
    PUBLIC_SERVANTS: { gain: "o salário rende mais", loss: "o salário rende menos" },
  },
  RETIREE_RAISE: { RETIREES: { gain: "o benefício rende mais", loss: "o benefício rende menos" } },
  PUBLIC_WORKS: {
    ENTREPRENEURS: { gain: "obras puxam os negócios", loss: "menos obra, menos negócio" },
    FORMAL_WORKERS: { gain: "obras criam vagas", loss: "menos obra, menos vaga" },
  },
};

/** O que a inflação e a SELIC mais altas tiram de cada grupo que não recebe o gasto. */
const INDIRECT_LOSS: Partial<Record<VoterGroup, string>> = {
  INVESTORS: "inflação, dívida e SELIC mais altas",
  RETIREES: "a inflação come o benefício",
  ENTREPRENEURS: "crédito mais caro com a SELIC",
};

/** O que a inflação e a SELIC mais baixas dão a cada grupo que não recebe o gasto. */
const INDIRECT_GAIN: Partial<Record<VoterGroup, string>> = {
  RETIREES: "o benefício rende mais",
  ENTREPRENEURS: "crédito mais barato com a SELIC",
};

/** Por que o grupo reage: o ganho ou a perda direta do grupo, ou o que a inflação e o consumo fazem com ele. */
export function reasonOf(kind: SpendingKind, group: VoterGroup, points: number, raising: boolean) {
  const direct = DIRECT_REASON[kind]?.[group];
  if (direct) return points > 0 ? direct.gain : direct.loss;
  if (raising) return points > 0 ? "mais consumo, mais vaga" : (INDIRECT_LOSS[group] ?? "inflação e SELIC mais altas");
  return points > 0 ? (INDIRECT_GAIN[group] ?? "inflação e dívida mais baixas") : "menos consumo, menos vaga";
}

export type ReactionSplit = { likes: GroupReaction[]; dislikes: GroupReaction[] };

/** Separa quem gosta (pontos positivos, do maior ao menor) de quem não gosta (negativos, do pior ao menos pior); grupo sem efeito fica de fora. */
export function splitReactions(reactions: readonly GroupReaction[]): ReactionSplit {
  const moved = reactions.filter((reaction) => Math.round(Number(reaction.points) * 10) !== 0);
  return {
    likes: moved.filter((reaction) => Number(reaction.points) > 0).sort((a, b) => Number(b.points) - Number(a.points)),
    dislikes: moved
      .filter((reaction) => Number(reaction.points) < 0)
      .sort((a, b) => Number(a.points) - Number(b.points)),
  };
}
