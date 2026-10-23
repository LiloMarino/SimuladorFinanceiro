import type { PlayerRef } from "@/types";

/** As linhas do ranking que ficam na tela: todas, ou só as de gente quando `onlyPeople`. A posição de cada linha segue a geral. */
export function visibleRankingRows<T extends Pick<PlayerRef, "is_bot">>(rows: T[], onlyPeople: boolean) {
  return onlyPeople ? rows.filter((row) => !row.is_bot) : rows;
}
