import type { MeasureKind } from "@/types";

export type SpendingKind = Extract<
  MeasureKind,
  "WELFARE_SPENDING" | "SERVANT_RAISE" | "RETIREE_RAISE" | "PUBLIC_WORKS"
>;

export const SPENDING_KINDS = [
  "WELFARE_SPENDING",
  "SERVANT_RAISE",
  "RETIREE_RAISE",
  "PUBLIC_WORKS",
] as const satisfies readonly SpendingKind[];

export const isSpending = (kind: MeasureKind): kind is SpendingKind => SPENDING_KINDS.includes(kind as SpendingKind);

export const SPENDING_LABEL: Record<SpendingKind, string> = {
  WELFARE_SPENDING: "Auxílio",
  SERVANT_RAISE: "Reajuste dos servidores",
  RETIREE_RAISE: "Reajuste das aposentadorias",
  PUBLIC_WORKS: "Obras",
};

/** O reajuste é ganho real ao ano; o auxílio e as obras são fatia do PIB. */
export const isRaise = (kind: SpendingKind) => kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE";
