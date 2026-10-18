import type { MetricInfo } from "@/shared/lib/metric-info";

export const P95_INFO: MetricInfo = {
  label: "p95",
  description: "O tempo que 95% das chamadas não passam.",
  definition:
    "p95: 95% das chamadas levam até esse tempo; só as 5% piores passam dele.",
  example:
    "Média de 20 ms com p95 de 400 ms quer dizer que quase sempre é rápida, mas de vez em quando trava.",
  reading: "Cada linha usa as últimas 1.000 chamadas dela.",
  format: (value) => String(value),
};
