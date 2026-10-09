import { displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { PlayerPerformance } from "@/types";

type RiskMetrics = PlayerPerformance["risk"];

export interface RiskMetric {
  key: keyof RiskMetrics;
  label: string;
  description: string;
  definition: string;
  example: string;
  reading: string;
  unavailable: string;
  format: (value: string) => string;
}

export const RISK_METRICS: RiskMetric[] = [
  {
    key: "max_drawdown",
    label: "Queda máxima",
    description: "Maior queda do patrimônio a partir de um pico",
    definition:
      "Drawdown máximo: a maior queda a partir de um pico, antes de recuperá-lo. Aportes não contam como recuperação.",
    example: "Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → 20%.",
    reading: "Quanto menor, melhor. Acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.",
    unavailable: "Aparece a partir do 2º dia de simulação.",
    format: (value) => displayPercent(value),
  },
  {
    key: "annual_volatility",
    label: "Volatilidade anual",
    description: "Quanto o patrimônio sobe e desce de um dia para o outro",
    definition:
      "Desvio-padrão dos retornos diários × √252 dias úteis: o tamanho típico da oscilação, em ritmo de um ano.",
    example: "Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.",
    reading: "Quanto menor, mais tranquilo o caminho. Não diz se o resultado foi bom, só o quanto balançou.",
    unavailable: "Aparece a partir do 3º dia de simulação.",
    format: (value) => displayPercent(value),
  },
  {
    key: "sharpe_ratio",
    label: "Índice de Sharpe",
    description: "Retorno acima do CDI por unidade de oscilação",
    definition: "(retorno anual − CDI anual) ÷ volatilidade anual. Mede se o risco corrido foi pago.",
    example: "Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → 0,50.",
    reading: "Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro.",
    unavailable: "Aparece a partir do 3º dia, quando o patrimônio oscila (carteira só em caixa não oscila).",
    format: (value) => displayNumber(value),
  },
];

export function displayRiskMetric(metric: RiskMetric, risk: RiskMetrics) {
  const value = risk[metric.key];
  return value === null ? "—" : metric.format(value);
}
