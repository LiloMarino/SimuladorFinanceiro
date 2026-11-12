import type { MetricInfo } from "@/shared/lib/metric-info";

// O Focus publica a mediana já em %, por isso o valor entra sem multiplicar
const publishedPercent = (value: string | number) =>
  `${Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;

const MEDIAN_DEFINITION =
  "O Focus é a pesquisa semanal em que o Banco Central pergunta a bancos e consultorias o que eles esperam da economia. A série guarda a mediana: o valor do meio, que metade das projeções passa e metade não alcança, e por isso um palpite fora da curva não a puxa.";

/** Como a partida trata o Focus: a série é importada e não ganha futuro gerado. */
export const FOCUS_IMPORT_NOTE =
  "Importada do Banco Central: não ganha futuro gerado. Sem pesquisa dos últimos 30 dias, a partida usa a SELIC da história.";

/** O que cada série do Focus mede, na dica ao lado do nome, pela chave da série. */
export const FOCUS_HINTS: Record<string, MetricInfo> = {
  FOCUS_SELIC: {
    label: "Focus: SELIC",
    description: "A SELIC que o mercado espera para a próxima reunião do Copom",
    definition: `${MEDIAN_DEFINITION} Aqui é a SELIC esperada para a primeira reunião do Copom ainda por vir. Na partida, a bolsa já tem esse valor no preço e reage só à surpresa: a decisão menos o esperado.`,
    example:
      "Ex.: o Focus espera 13,25% e o Copom decide 12,25%: foi 1 ponto abaixo do esperado, e a bolsa sobe uns 3% no dia em que a decisão passa a valer.",
    reading:
      "Decisão igual ao Focus não mexe na bolsa; acima do esperado ela cai, abaixo ela sobe. Os 3% do exemplo vêm de 2,9% por ponto de surpresa. Antes de nov/2004 a série não existe, e a partida usa a SELIC da história.",
    format: publishedPercent,
  },
  FOCUS_IPCA: {
    label: "Focus: IPCA em 12 meses",
    description: "A inflação que o mercado espera para os próximos 12 meses",
    definition: `${MEDIAN_DEFINITION} Aqui é o IPCA, a inflação oficial, esperado para os próximos 12 meses, na versão suavizada, que não dá saltos quando o ano vira.`,
    example: "Ex.: 4,50% quer dizer que, para a maioria do mercado, os preços sobem uns 4,5% até daqui a um ano.",
    reading:
      "Perto da meta de inflação (3%) é tranquilo; acima de 6% o mercado teme que o Banco Central perca o controle e tende a pedir juro mais alto.",
    format: publishedPercent,
  },
  FOCUS_GDP: {
    label: "Focus: PIB do ano",
    description: "O crescimento da economia que o mercado espera para o ano da pesquisa",
    definition: `${MEDIAN_DEFINITION} Aqui é o crescimento do PIB, tudo o que o país produz, esperado para o ano em que a pesquisa foi feita.`,
    example: "Ex.: 2,00% quer dizer que o país deve produzir 2% a mais neste ano do que no anterior.",
    reading:
      "Perto de 2% é o ritmo normal; acima de 3% o mercado vê a economia aquecida; abaixo de 0% espera recessão.",
    format: publishedPercent,
  },
  FOCUS_FX: {
    label: "Focus: câmbio do fim do ano",
    description: "O dólar, em reais, que o mercado espera para o fim do ano da pesquisa",
    definition: `${MEDIAN_DEFINITION} Aqui é a cotação do dólar esperada para dezembro do ano em que a pesquisa foi feita; o valor guardado é em reais por dólar, como publicado.`,
    example: "Ex.: 5,20 quer dizer que o mercado espera pagar R$ 5,20 por dólar no fim do ano.",
    reading:
      "Compare com o dólar de hoje: esperado acima dele é o mercado apostando em real mais fraco; abaixo, em real mais forte.",
    format: (value) => Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
  },
};
