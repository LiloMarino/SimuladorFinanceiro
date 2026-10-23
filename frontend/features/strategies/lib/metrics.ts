import type { MetricInfo } from "@/shared/lib/metric-info";
import { displaySignedPercent } from "@/shared/lib/utils/display";

export const STRATEGY_RETURN: MetricInfo = {
  label: "Patrimônio desde que ligou",
  description: "Quanto o patrimônio cresceu desde que a estratégia começou",
  definition:
    "A variação do seu patrimônio (caixa, ações e renda fixa) entre o dia em que você ligou o automático e hoje, sem contar os aportes que você fez no caminho.",
  example: "Ex.: ligou com R$ 100.000 e hoje tem R$ 103.820 → +3,82%.",
  reading:
    "Compare com o Ibovespa no mesmo período: acima dele, a estratégia está ganhando do mercado; abaixo, o mercado fez melhor. Poucos dias de amostra dizem pouco.",
  format: (value) => displaySignedPercent(value),
};

export const IBOVESPA_SAME_PERIOD: MetricInfo = {
  label: "Ibovespa",
  description: "A régua do mercado",
  definition:
    "O índice que acompanha as maiores ações da bolsa, medido nos mesmos dias em que a estratégia esteve ligada.",
  example: "Ex.: o Ibovespa caiu 1,20% desde o dia em que você ligou, enquanto o seu patrimônio subiu 3,82%.",
  reading:
    "Estar acima do Ibovespa é bom; estar abaixo não é erro, mas mostra que comprar o índice teria rendido mais.",
  format: (value) => displaySignedPercent(value),
};
