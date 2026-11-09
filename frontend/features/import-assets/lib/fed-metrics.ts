import type { MetricInfo } from "@/shared/lib/metric-info";

/** A série do juro americano, na dica ao lado do nome. O FRED publica o valor já em %. */
export const FED_FUNDS_HINT: MetricInfo = {
  label: "Fed Funds",
  description: "O juro básico dos Estados Unidos, ao ano",
  definition:
    "A taxa de juros que o banco central americano (o Fed) fixa para os empréstimos entre bancos. É o que a conta em dólar rende. A série vem do FRED, a base de dados do banco central de St. Louis, com um valor por dia.",
  example: "Ex.: 5,25% quer dizer que US$ 1.000 rendem uns US$ 52,50 em um ano.",
  reading:
    "Quanto maior, mais a conta em dólar rende. Costuma ser bem menor que o CDI: em 2021 ficou perto de 0%, em 2023 passou de 5%. Para o futuro, a série volta para 3% ao ano, a projeção de longo prazo do próprio Fed, perdendo metade da distância a cada 2 anos.",
  format: (value) =>
    `${Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`,
};
