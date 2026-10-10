import { displayNumber } from "@/shared/lib/utils/display";
import type { MetricInfo } from "@/shared/lib/metric-info";
import type { CorrelationWindow } from "@/types";

export const CORRELATION: MetricInfo = {
  label: "Correlação",
  description: "Quanto dois ativos sobem e caem nos mesmos dias, de −1 a 1",
  definition:
    "A correlação de Pearson entre os retornos diários de dois ativos: mede se, nos dias em que um sobe mais que o normal, o outro também sobe.",
  example:
    "Ex.: dois bancos como ITUB4 e BBDC4 ficam perto de 0,8, porque as mesmas notícias movem os dois.",
  reading:
    "Perto de 1, os dois andam juntos e somam a mesma aposta; perto de 0, um não diz nada sobre o outro; negativa, um tende a subir quando o outro cai. Para diversificar, quanto mais baixa, melhor.",
  format: (value) => displayNumber(value),
};

export const COMMON_DAYS: MetricInfo = {
  label: "Pregões em comum",
  description: "Quantos dias com retorno dos dois ativos entraram no cálculo",
  definition:
    "Cada par usa só os pregões em que os dois ativos negociaram, então a amostra muda de célula para célula: uma ação listada há pouco tempo tem menos dias em comum com as outras.",
  example: "Ex.: 126 pregões são ~6 meses; 252 pregões, um ano.",
  reading: "Com menos de 63 pregões (~3 meses), a correlação muda muito de uma janela para outra; leia com cautela.",
  format: (value) => `${value} pregões`,
};

export const WINDOWS: { value: CorrelationWindow; label: string }[] = [
  { value: "6m", label: "6 meses" },
  { value: "1y", label: "1 ano" },
  { value: "3y", label: "3 anos" },
  { value: "5y", label: "5 anos" },
];

export const READING_BANDS = [
  { min: 0.7, label: "andam muito juntos" },
  { min: 0.3, label: "andam juntos em parte" },
  { min: -0.3, label: "quase independentes" },
  { min: -Infinity, label: "tendem a ir em direções opostas" },
] as const;

/** Faixa de leitura de uma correlação; as faixas vão da mais alta para a mais baixa. */
export function correlationReading(value: number) {
  return READING_BANDS.find((band) => value >= band.min)!.label;
}
