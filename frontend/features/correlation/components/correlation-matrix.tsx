import { cn } from "@/shared/lib/utils";
import { displayNumber } from "@/shared/lib/utils/display";
import type { CorrelationMatrix } from "@/types";
import { REFERENCE, cellColor } from "../lib/correlation";

export interface PairPosition {
  row: number;
  column: number;
}

interface CorrelationMatrixGridProps {
  matrix: CorrelationMatrix;
  pinned: PairPosition | null;
  onPin: (pair: PairPosition) => void;
}

/**
 * Só a metade de baixo: a de cima repete a mesma conta e a diagonal é sempre 1. O
 * Ibovespa fica numa linha à parte, como referência de cada ativo contra o mercado.
 */
export function CorrelationMatrixGrid({ matrix, pinned, onPin }: CorrelationMatrixGridProps) {
  const { labels, rows } = matrix;
  const reference = labels.indexOf(REFERENCE);
  const tickers = labels.filter((l) => l !== REFERENCE);

  const cell = (row: number, column: number) => {
    const value = rows[row][column].correlation;
    const number = value === null ? null : Number(value);
    const active = pinned?.row === row && pinned.column === column;
    return (
      <td key={column} className="p-0.5">
        <button
          type="button"
          onClick={() => onPin({ row, column })}
          aria-pressed={active}
          aria-label={`${labels[row]} × ${labels[column]}`}
          className={cn(
            "grid h-11 w-full min-w-14 place-content-center rounded-md font-mono text-[13px] transition-shadow",
            number === null && "border border-dashed border-input text-faint-foreground",
            number !== null && Math.abs(number) > 0.6 && "text-white",
            active && "ring-2 ring-foreground ring-offset-1",
          )}
          style={number !== null ? { backgroundColor: cellColor(number) } : undefined}
        >
          {number === null ? "—" : displayNumber(number)}
        </button>
      </td>
    );
  };

  return (
    <div className="grid gap-4">
      <div className="overflow-x-auto">
        <table className="w-full border-separate border-spacing-0">
          <thead>
            <tr>
              <th />
              {tickers.map((t) => (
                <th key={t} scope="col" className="px-1 pb-1.5 font-mono text-xs font-medium text-muted-foreground">
                  {t}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tickers.slice(1).map((t, k) => {
              const row = labels.indexOf(t);
              return (
                <tr key={t}>
                  <th scope="row" className="pr-2 text-right font-mono text-xs font-medium text-muted-foreground">
                    {t}
                  </th>
                  {tickers.map((other, j) => (j <= k ? cell(row, labels.indexOf(other)) : <td key={other} />))}
                </tr>
              );
            })}
            {/* Ibovespa */}
            <tr>
              <th scope="row" className="pt-3 pr-2 text-right text-xs font-semibold">
                Ibovespa
              </th>
              {tickers.map((t) => cell(reference, labels.indexOf(t)))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Legenda */}
      <div className="grid w-80 max-w-full gap-1">
        <div
          className="h-2 rounded-full"
          style={{ background: `linear-gradient(to right, ${cellColor(-1)}, transparent, ${cellColor(1)})` }}
        />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>−1 opostos</span>
          <span>0 independentes</span>
          <span>1 juntos</span>
        </div>
      </div>
    </div>
  );
}
