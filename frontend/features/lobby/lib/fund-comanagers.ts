import type { MyPreparation } from "@/types";

/** Um convidado a co-gestor da gestora que o jogador funda. */
export type FundComanagerRow = MyPreparation["fund_comanagers"][number];

/** A parte das taxas como a tela mostra: a fração da API (0,2) vira "20%". */
export const sharePercent = (share: string) => `${Number((Number(share) * 100).toFixed(2))}%`;

/** Os convites que ocupam vaga e reservam parte: o recusado não conta. */
export const openComanagers = (comanagers: FundComanagerRow[]) => comanagers.filter((c) => c.status !== "DECLINED");

/** O que os convites abertos já reservam das taxas, em pontos percentuais. */
export const reservedPoints = (comanagers: FundComanagerRow[]) =>
  Math.round(openComanagers(comanagers).reduce((sum, c) => sum + Number(c.share), 0) * 100);

/** Pontos percentuais inteiros no formato da API (20 vira "0.2"). */
export const pointsToShare = (points: number) => String(points / 100);
