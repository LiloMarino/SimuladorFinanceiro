import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayNumber } from "@/shared/lib/utils/display";

/** Pontos inteiros com a unidade: 1240 → "1.240 pts". */
export const displayPoints = (value: string | number) => `${displayNumber(value, 0)} pts`;

export const POLITICAL_CAPITAL: MetricInfo = {
  label: "Capital político",
  description: "Pontos que o partido soma a cada mês fechado",
  definition:
    "Cada mês fechado rende pontos ao partido: 1 por cadeira no Congresso e, para o partido do presidente, a aprovação do governo (0 a 100). No balanço do fim do mandato, cada promessa cumprida por inteiro vale 100 pontos, proporcional ao que foi cumprido. O impeachment tira metade do que a presidência rendeu no mandato. Só partidos de jogadores pontuam.",
  example:
    "Ex.: 28 cadeiras e aprovação 62 rendem 28 + 62 = 90 pontos no mês. No fim do mandato, 2 promessas inteiras e 1 pela metade somam 250. Se a presidência rendeu 620 e houve impeachment, o partido perde 310.",
  reading:
    "Mais pontos é melhor: o partido com mais pontos vence a partida política, e os filiados vencem juntos. Os pontos só crescem com o tempo, a não ser pelo impeachment. Empatando, vence quem tem mais cadeiras na casa atual.",
  format: displayPoints,
};
