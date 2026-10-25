import type { TopicId } from "@/features/tutorial/lib/topics";

/** Texto de uma métrica: a descrição curta fica ao lado do número; o resto vai na dica. */
export interface MetricInfo {
  label: string;
  description: string;
  definition: string;
  example: string;
  reading: string;
  format: (value: string | number) => string;
  /** Tópico do Como jogar que explica a métrica por inteiro; a dica passa a abrir no clique, com o link. */
  topic?: TopicId;
}
