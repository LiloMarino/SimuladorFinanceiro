/** As ajudas que a partida pode esconder; o Modo Especialista é todas escondidas. */
export const ASSISTANCES = [
  {
    field: "showEquivalentRate",
    label: "Esconder taxa equivalente",
    description: "Esconde a taxa por ano de cada título e a ordenação da lista por ela.",
    scope: "Renda fixa · lista e detalhe",
  },
  {
    field: "showMaturityProjection",
    label: "Esconder projeção no vencimento",
    description: "Esconde quanto o valor investido vira no vencimento, com o IR já descontado.",
    scope: "Renda fixa · detalhe e compra",
  },
  {
    field: "showChartHints",
    label: "Esconder dicas de análise técnica",
    description:
      "Esconde os padrões de vela, as legendas dos indicadores e o desafio da vela: você lê o gráfico sozinho.",
    scope: "Renda variável · gráfico",
  },
] as const;

export type AssistanceField = (typeof ASSISTANCES)[number]["field"];

type AssistanceMode = "NORMAL" | "EXPERT" | "CUSTOM";

export type AssistanceSummary = {
  mode: AssistanceMode;
  /** Quantas ajudas seguem aparecendo */
  shown: number;
  total: number;
};

/** O modo vem das ajudas: todas aparecendo é Normal, todas escondidas é Especialista, o resto é Personalizado. */
export function summarizeAssistances(shown: readonly boolean[]): AssistanceSummary {
  const count = shown.filter(Boolean).length;
  const mode = count === shown.length ? "NORMAL" : count === 0 ? "EXPERT" : "CUSTOM";
  return { mode, shown: count, total: shown.length };
}
