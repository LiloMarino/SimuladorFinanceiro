import type { VictoryCriterion } from "@/types";

/** O que decide a partida: escolhido no lobby, ordena o ranking e o pódio. */
export const VICTORY_CRITERIA: Record<VictoryCriterion, { label: string; description: string }> = {
  SCORE: {
    label: "Nota geral",
    description: "Retorno, risco, consistência e eficiência num número só. Quem ainda não tem nota fica atrás.",
  },
  RETURN: {
    label: "Rentabilidade",
    description: "O maior retorno sobre o capital aportado, sem olhar o risco corrido.",
  },
  NETWORTH: {
    label: "Patrimônio final",
    description: "O maior patrimônio no último dia. Com aportes iguais, é o mesmo que a rentabilidade.",
  },
  SHARPE: {
    label: "Índice de Sharpe",
    description: "O maior retorno acima do CDI por unidade de oscilação: premia ganhar sem sobressaltos.",
  },
};
