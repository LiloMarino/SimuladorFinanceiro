import { ASSET_CLASS_LABELS } from "@/shared/lib/asset-class";
import type { AssetClass } from "@/types";
import type { NetworthPoint } from "./networth-model";

export type PanelConfig = {
  key: string;
  label: string;
  color: string;
  lineClass: string;
  areaClass: string;
  dotClass: string;
  valueOf: (point: NetworthPoint) => number;
};

type PanelStyle = Pick<PanelConfig, "color" | "lineClass" | "areaClass" | "dotClass">;

export const CLASS_PANELS: PanelConfig[] = [
  {
    key: "equity",
    label: "Renda variável",
    color: "var(--chart-1)",
    lineClass: "stroke-chart-1",
    areaClass: "fill-chart-1/12",
    dotClass: "stroke-chart-1",
    valueOf: (p) => p.equity,
  },
  {
    key: "fixed",
    label: "Renda fixa",
    color: "var(--chart-2)",
    lineClass: "stroke-chart-2",
    areaClass: "fill-chart-2/12",
    dotClass: "stroke-chart-2",
    valueOf: (p) => p.fixed,
  },
  {
    key: "cash",
    label: "Caixa",
    color: "var(--faint-foreground)",
    lineClass: "stroke-faint-foreground",
    areaClass: "fill-faint-foreground/12",
    dotClass: "stroke-faint-foreground",
    valueOf: (p) => p.cash,
  },
];

const TYPE_STYLES: Record<AssetClass, PanelStyle> = {
  STOCK: {
    color: "var(--chart-1)",
    lineClass: "stroke-chart-1",
    areaClass: "fill-chart-1/12",
    dotClass: "stroke-chart-1",
  },
  FII: {
    color: "var(--chart-3)",
    lineClass: "stroke-chart-3",
    areaClass: "fill-chart-3/12",
    dotClass: "stroke-chart-3",
  },
  ETF: {
    color: "var(--chart-4)",
    lineClass: "stroke-chart-4",
    areaClass: "fill-chart-4/12",
    dotClass: "stroke-chart-4",
  },
  BDR: {
    color: "var(--chart-5)",
    lineClass: "stroke-chart-5",
    areaClass: "fill-chart-5/12",
    dotClass: "stroke-chart-5",
  },
  CRYPTO: {
    color: "var(--chart-6)",
    lineClass: "stroke-chart-6",
    areaClass: "fill-chart-6/12",
    dotClass: "stroke-chart-6",
  },
  FUND: {
    color: "var(--chart-2)",
    lineClass: "stroke-chart-2",
    areaClass: "fill-chart-2/12",
    dotClass: "stroke-chart-2",
  },
};

/** Um painel por tipo de renda variável; o dia sem o tipo em carteira vale zero. */
export function typePanels(types: AssetClass[]): PanelConfig[] {
  return types.map((type) => ({
    key: type,
    label: ASSET_CLASS_LABELS[type],
    ...TYPE_STYLES[type],
    valueOf: (p) => p.equityByClass?.[type] ?? 0,
  }));
}
