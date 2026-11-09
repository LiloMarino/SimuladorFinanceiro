import type { MeasureKind } from "@/types";

export type SpendingKind = Extract<
  MeasureKind,
  "WELFARE_SPENDING" | "SERVANT_RAISE" | "RETIREE_RAISE" | "PUBLIC_WORKS" | "OPERATING_COST"
>;

export const SPENDING_KINDS = [
  "WELFARE_SPENDING",
  "SERVANT_RAISE",
  "RETIREE_RAISE",
  "PUBLIC_WORKS",
  "OPERATING_COST",
] as const satisfies readonly SpendingKind[];

export const isSpending = (kind: MeasureKind): kind is SpendingKind => SPENDING_KINDS.includes(kind as SpendingKind);

export const SPENDING_LABEL: Record<SpendingKind, string> = {
  WELFARE_SPENDING: "Auxílio",
  SERVANT_RAISE: "Reajuste dos servidores",
  RETIREE_RAISE: "Reajuste das aposentadorias",
  PUBLIC_WORKS: "Obras",
  OPERATING_COST: "Custeio",
};

/** O reajuste é ganho real ao ano; o auxílio, as obras e o custeio são fatia do PIB. */
export const isRaise = (kind: SpendingKind) => kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE";

/** Só o auxílio e as obras viram programa com nome. */
export const isNameable = (kind: SpendingKind) => kind === "WELFARE_SPENDING" || kind === "PUBLIC_WORKS";
