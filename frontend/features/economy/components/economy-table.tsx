import { Card, CardContent } from "@/shared/components/ui/card";
import { displayDate, displayPercent, parseLocalDate } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";

type EconomyTableProps = { panel: EconomyPanel };

/** Os mesmos números do gráfico em tabela, do mês mais recente para o mais antigo. */
export function EconomyTable({ panel }: EconomyTableProps) {
  const points = [...panel.points].reverse();

  return (
    <Card>
      <CardContent>
        <details>
          <summary className="cursor-pointer text-[15px] font-semibold">Ver como tabela</summary>
          <div className="mt-3 max-h-80 overflow-auto">
            <table className="w-full text-[13px]">
              <thead className="sticky top-0 bg-card text-left text-xs text-muted-foreground">
                <tr>
                  <th className="py-1.5 pr-3 font-medium">Data</th>
                  <th className="px-3 py-1.5 text-right font-medium">SELIC</th>
                  <th className="px-3 py-1.5 text-right font-medium">IPCA em 12 meses</th>
                  <th className="px-3 py-1.5 text-right font-medium">Juro real</th>
                  <th className="py-1.5 pl-3 text-right font-medium">Meta do ano</th>
                </tr>
              </thead>
              <tbody>
                {points.map((point) => (
                  <tr key={point.date} className="border-t">
                    <td className="py-1.5 pr-3">{displayDate(parseLocalDate(point.date))}</td>
                    <td className="px-3 py-1.5 text-right font-mono">{displayPercent(point.selic, 2)}</td>
                    <td className="px-3 py-1.5 text-right font-mono">{displayPercent(point.ipca, 2)}</td>
                    <td className="px-3 py-1.5 text-right font-mono">{displayPercent(point.real_rate, 2)}</td>
                    <td className="py-1.5 pl-3 text-right font-mono">{displayPercent(point.target, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </CardContent>
    </Card>
  );
}
