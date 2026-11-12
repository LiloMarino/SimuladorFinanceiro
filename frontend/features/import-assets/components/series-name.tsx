import type { ReactNode } from "react";
import type { SeriesCoverage } from "@/types";
import { CorrectedDaysHint } from "./corrected-days-hint";

type SeriesNameProps = {
  series: SeriesCoverage;
  /** O indicador abre pelo nome e o ativo pelo código: é o que cada um chama de "o nome" */
  order: "name-first" | "code-first";
  /** Dica ao lado do primeiro texto */
  hint?: ReactNode;
  /** Texto da linha de baixo, depois do código quando ele aparece ali */
  note?: ReactNode;
  /** Bloco abaixo das duas linhas */
  children?: ReactNode;
};

/** A identificação da série: o nome completo quebra em linhas, nada é cortado. */
export function SeriesName({ series, order, hint, note, children }: SeriesNameProps) {
  const code = <span className="font-mono">{series.key}</span>;
  const hasName = series.name !== series.key;

  return (
    <div className="grid min-w-0 gap-0.5 whitespace-normal">
      <div className="flex items-start gap-1.5 text-sm leading-snug font-semibold">
        <span className="min-w-0 break-words">{order === "code-first" ? code : series.name}</span>
        {hint}
        <CorrectedDaysHint days={series.corrected_days} />
      </div>
      {order === "code-first"
        ? hasName && <span className="text-xs leading-snug break-words text-foreground">{series.name}</span>
        : (hasName || note) && (
            <span className="text-xs leading-snug break-words text-muted-foreground">
              {hasName && <span className="font-mono">{series.key}</span>}
              {hasName && note && " · "}
              {note}
            </span>
          )}
      {children}
    </div>
  );
}
