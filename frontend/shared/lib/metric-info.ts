/** Texto de uma métrica: a descrição curta fica ao lado do número; o resto vai na dica. */
export interface MetricInfo {
  label: string;
  description: string;
  definition: string;
  example: string;
  reading: string;
  format: (value: string | number) => string;
}
