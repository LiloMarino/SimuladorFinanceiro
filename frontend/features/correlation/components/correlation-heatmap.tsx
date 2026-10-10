import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import { displayNumber } from "@/shared/lib/utils/display";
import type { CorrelationCell, CorrelationMatrix } from "@/types";
import { correlationReading } from "../lib/correlation";

interface CorrelationHeatmapProps {
  matrix: CorrelationMatrix;
}

/** Fundo da célula: vermelho para correlação positiva (ruim para diversificar), azul para negativa. */
function cellColor(value: number) {
  const token = value >= 0 ? "--destructive" : "--chart-1";
  return `color-mix(in oklch, var(${token}) ${Math.round(Math.abs(value) * 70)}%, transparent)`;
}

function cellText(row: string, column: string, cell: CorrelationCell, minDays: number) {
  if (cell.correlation === null) {
    return cell.days < minDays
      ? `${row} × ${column}: só ${cell.days} pregões em comum; o mínimo é ${minDays}.`
      : `${row} × ${column}: um dos dois ficou parado na janela, então não há como medir se andam juntos.`;
  }
  const value = Number(cell.correlation);
  return `${row} × ${column}: ${displayNumber(value)}, ${correlationReading(value)} · ${cell.days} pregões em comum`;
}

export function CorrelationHeatmap({ matrix }: CorrelationHeatmapProps) {
  const { labels, rows, min_days: minDays } = matrix;

  return (
    <div className="space-y-4">
      {/* Grade */}
      <div className="overflow-x-auto">
        <table className="border-separate border-spacing-1 text-sm">
          <thead>
            <tr>
              <th />
              {labels.map((label) => (
                <th key={label} scope="col" className="px-1 pb-1 text-xs font-medium text-muted-foreground">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((cells, i) => (
              <tr key={labels[i]}>
                <th scope="row" className="pr-2 text-right text-xs font-medium text-muted-foreground">
                  {labels[i]}
                </th>
                {cells.map((cell, j) => {
                  const value = cell.correlation === null ? null : Number(cell.correlation);
                  const diagonal = i === j && value !== null;
                  return (
                    <td key={labels[j]} className="p-0">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div
                            tabIndex={0}
                            className={cn(
                              "flex h-12 w-16 items-center justify-center rounded-md tabular-nums",
                              diagonal && "bg-muted text-muted-foreground",
                              value === null && "border border-dashed text-muted-foreground",
                            )}
                            style={!diagonal && value !== null ? { backgroundColor: cellColor(value) } : undefined}
                          >
                            {value === null ? "—" : displayNumber(value)}
                          </div>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-72">
                          {diagonal
                            ? `${labels[i]} com ele mesmo: sempre 1 · ${cell.days} pregões com retorno`
                            : cellText(labels[i], labels[j], cell, minDays)}
                        </TooltipContent>
                      </Tooltip>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legenda */}
      <div className="max-w-sm space-y-1">
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
