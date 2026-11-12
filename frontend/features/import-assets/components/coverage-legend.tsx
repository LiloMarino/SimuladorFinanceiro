import type { ReactNode } from "react";
import { cn } from "@/shared/lib/utils";
import { FUTURE_DOCS_URL } from "../lib/future-readings";

/** Amostra de cada trecho da barra: o desenho é o mesmo da `CoverageBar`. */
const SWATCH = {
  real: "bg-primary",
  repeat: "bg-[repeating-linear-gradient(135deg,var(--chart-3)_0_3px,transparent_3px_6px)] opacity-70",
  generated: "bg-chart-3",
  computed: "bg-chart-2",
  none: "bg-muted ring-1 ring-border ring-inset",
} as const;

export function Swatch({ kind }: { kind: keyof typeof SWATCH }) {
  return <span className={cn("inline-block h-2.5 w-7 shrink-0 rounded-full", SWATCH[kind])} />;
}

function LegendItem({ children, swatch }: { children: ReactNode; swatch: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2">
      {children}
      {swatch}
    </span>
  );
}

/** A legenda da barra no topo da aba de indicadores. */
export function CoverageLegend() {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t px-4 py-2.5 text-[13px] text-muted-foreground">
      <b className="font-semibold text-foreground">Como ler a barra</b>
      <LegendItem swatch={<Swatch kind="real" />}>Dado real</LegendItem>
      <LegendItem swatch={<Swatch kind="repeat" />}>Sem futuro gerado ainda: repete o último valor</LegendItem>
      <LegendItem swatch={<span className="h-3 w-0.5 bg-foreground" />}>Hoje</LegendItem>
      <LegendItem swatch={<Swatch kind="generated" />}>Futuro gerado</LegendItem>
      <LegendItem swatch={<Swatch kind="computed" />}>Calculado na partida</LegendItem>
      <a href={FUTURE_DOCS_URL} target="_blank" rel="noreferrer" className="ml-auto font-medium text-primary">
        Como o futuro é gerado
      </a>
    </div>
  );
}
