import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { MetricHint } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayList, displayNumber } from "@/shared/lib/utils/display";
import type { CorrelationMatrix } from "@/types";
import { COMMON_DAYS, REFERENCE, correlationReading, gapReason } from "../lib/correlation";
import type { PairPosition } from "./correlation-matrix";

const valueTone = (value: number) => (value >= 0.3 ? "text-destructive" : value <= -0.3 ? "text-chart-1" : undefined);

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

const nameOf = (label: string) => (label === REFERENCE ? "Ibovespa" : label);

/** O par clicado na matriz: o número, a leitura e quantos pregões entraram; sem número, o motivo. */
function SelectedPair({ matrix, pinned }: { matrix: CorrelationMatrix; pinned: PairPosition | null }) {
  if (!pinned) {
    return (
      <div className="rounded-[10px] bg-subtle p-3.5 text-[13px] text-muted-foreground">
        Clique numa célula da matriz pra ver o par aqui.
      </div>
    );
  }
  const cell = matrix.rows[pinned.row][pinned.column];
  const value = cell.correlation === null ? null : Number(cell.correlation);

  return (
    <div className="grid gap-1.5 rounded-[10px] bg-subtle p-3.5">
      <span className="text-[11px] font-semibold tracking-[0.06em] text-faint-foreground uppercase">Selecionado</span>
      <span className="font-semibold">
        {nameOf(matrix.labels[pinned.row])} × {nameOf(matrix.labels[pinned.column])}
      </span>
      {value === null ? (
        <>
          <span className="font-mono text-[22px] font-semibold text-faint-foreground">—</span>
          <span className="text-[13px] text-muted-foreground">{gapReason(cell, matrix.min_days)}</span>
        </>
      ) : (
        <>
          <span className={cn("font-mono text-[22px] font-semibold", valueTone(value))}>{displayNumber(value)}</span>
          <span className="text-[13px]">
            {capitalize(correlationReading(value))} · <span className="font-mono">{cell.days}</span> pregões em comum{" "}
            <span className="inline-flex align-middle">
              <MetricHint metric={COMMON_DAYS} />
            </span>
          </span>
        </>
      )}
    </div>
  );
}

function Highlight({ label, names, value, note }: { label: string; names: string; value: string; note: string }) {
  return (
    <div className="grid gap-1 border-t border-muted py-3">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className="flex justify-between gap-2 font-semibold">
        <span>{names}</span>
        <span className={cn("font-mono", valueTone(Number(value)))}>{displayNumber(value)}</span>
      </span>
      <span className="text-xs text-muted-foreground">{note}</span>
    </div>
  );
}

/** Ao lado da matriz: o par fixado e os destaques entre os ativos escolhidos. */
export function CorrelationSidePanel({ matrix, pinned }: { matrix: CorrelationMatrix; pinned: PairPosition | null }) {
  const { most_similar: similar, best_diversifier: diversifier, portfolio } = matrix.highlights;

  return (
    <Card size="sm">
      <CardContent>
        <SelectedPair matrix={matrix} pinned={pinned} />
      </CardContent>
      <CardHeader>
        <CardTitle>Destaques</CardTitle>
      </CardHeader>
      <CardContent>
        {!similar && !portfolio ? (
          <p className="text-[13px] text-muted-foreground">Os destaques aparecem com dois ou mais ativos medidos.</p>
        ) : (
          <div className="grid">
            {similar && (
              <Highlight
                label="Mais parecidos"
                names={`${similar.first} e ${similar.second}`}
                value={similar.correlation}
                note={`${capitalize(correlationReading(Number(similar.correlation)))}: ter os dois é quase a mesma aposta quanto mais perto de 1.`}
              />
            )}
            {diversifier &&
              !(similar && diversifier.first === similar.first && diversifier.second === similar.second) && (
                <Highlight
                  label="Melhor par pra diversificar"
                  names={`${diversifier.first} e ${diversifier.second}`}
                  value={diversifier.correlation}
                  note={`${capitalize(correlationReading(Number(diversifier.correlation)))}: quando um cai, o outro tende a não cair junto.`}
                />
              )}
            {portfolio && (
              <Highlight
                label="Sua carteira"
                names={displayList(portfolio.tickers)}
                value={portfolio.average}
                note={`Correlação média entre as suas ações: ${correlationReading(Number(portfolio.average))}.`}
              />
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
