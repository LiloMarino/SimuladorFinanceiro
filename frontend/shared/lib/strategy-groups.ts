import type { StrategyGroup } from "@/types";

/** Título e dica de cada grupo na lista de estratégias. */
export const GROUP_SECTION: Record<StrategyGroup, { title: string; hint: string }> = {
  reference: {
    title: "Referências",
    hint: "Estratégias simples, sem parâmetros de risco, que servem de régua: se a sua não rende mais do que elas, o trabalho extra não compensou.",
  },
  tactic: {
    title: "Táticas",
    hint: "Regras que reagem ao preço e escolhem quando comprar e vender. Têm parâmetros que você ajusta e vê no gráfico antes de salvar.",
  },
};
