import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber, type SortColumns } from "@/shared/lib/table-sort";
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
  const columns: SortColumns<string> = { asset: (ticker) => ticker };
  for (const label of labels) {
    columns[`correlation:${label}`] = (ticker) => sortNumber(rows[labels.indexOf(ticker)][labels.indexOf(label)].correlation);
  }
  const sorting = useTableSort(labels.filter((l) => l !== REFERENCE), columns);
  const tickers = sorting.rows;

  const cell = (row: number, column: number) => {
    const value = rows[row][column].correlation;
    const number = value === null ? null : Number(value);
    const active = !!pinned && ((pinned.row === row && pinned.column === column)
      || (pinned.row === column && pinned.column === row));
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
          <caption className="pb-2 text-left text-xs text-muted-foreground">
            Clique nos cabeçalhos para ordenar por ativo ou correlação. Os dois eixos acompanham a ordem.
          </caption>
          <thead>
            <tr>
              <SortableTableHead label="Ativo" {...sorting.header("asset")} variant="matrix" />
              {tickers.map((t) => (
                <SortableTableHead key={t} label={t} {...sorting.header(`correlation:${t}`)} variant="matrix" />
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
                <button type="button" onClick={sorting.header(`correlation:${REFERENCE}`).onSort}
                  aria-label={`Ordenar pela correlação com Ibovespa, ordem ${sorting.sort?.column === `correlation:${REFERENCE}` && sorting.sort.direction === "asc" ? "decrescente" : "crescente"}`}
                  className="inline-flex min-h-9 items-center gap-1 rounded-sm focus-visible:ring-2 focus-visible:ring-ring">
                  Ibovespa {sorting.sort?.column === `correlation:${REFERENCE}` ? (sorting.sort.direction === "asc" ? "↑" : "↓") : "↕"}
                </button>
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
