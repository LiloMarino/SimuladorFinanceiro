import { Plus } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { GovernmentPanel, MeasureKind } from "@/types";
import { useToday } from "../hooks/useToday";
import { generalLabel, generalToday, isGeneral, measureTarget, monthYear, sectorEffect } from "../lib/government";

type TaxesCardProps = {
  panel: GovernmentPanel;
  onPropose: (kind?: MeasureKind) => void;
};

/** Os impostos em vigor hoje e as medidas por setor; o presidente propõe a mudança de cada linha. */
export function TaxesCard({ panel, onPropose }: TaxesCardProps) {
  const today = useToday(panel);
  const baseRate = panel.taxes.find((row) => row.kind === "STOCK_PROFIT_RATE")?.value ?? "0";

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="flex items-center justify-between gap-3">
            <div className="grid gap-0.5">
              <h2 className="text-[15px] font-semibold">Impostos</h2>
              <span className="text-xs text-muted-foreground">
                Imposto não mexe em preço: muda quanto cada um paga ao vender com lucro.
              </span>
            </div>
            {panel.is_president && (
              <Button size="sm" onClick={() => onPropose()}>
                <Plus />
                Nova medida
              </Button>
            )}
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Imposto</TableHead>
                <TableHead numeric>Hoje</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {panel.taxes.map((row) => {
                const kind = row.kind;
                if (!isGeneral(kind)) return null;
                return (
                  <TableRow key={kind}>
                    <TableCell className="whitespace-normal">{generalLabel(kind, row.value)}</TableCell>
                    <TableCell numeric>{generalToday(kind, row.value, row.top_value)}</TableCell>
                    <TableCell numeric>
                      {row.pending ? (
                        <Badge variant="warning" size="sm">
                          {row.pending.status === "QUEUED" || !row.pending.effective
                            ? "na fila"
                            : `vale em ${displayDayMonth(row.pending.effective)}`}
                        </Badge>
                      ) : (
                        panel.is_president && (
                          <Button size="xs" variant="outline" onClick={() => onPropose(kind)}>
                            Mudar
                          </Button>
                        )
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}

              {/* Medidas por setor */}
              <TableRow variant="group">
                <TableCell colSpan={3} variant="group">
                  Medidas por setor
                </TableCell>
              </TableRow>
              {panel.sector_measures.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3} variant="note">
                    Nenhum setor com regra própria. O presidente pode taxar ou isentar um setor ou segmento.
                  </TableCell>
                </TableRow>
              )}
              {panel.sector_measures.map(({ measure, assets }) => {
                const waiting = measure.effective !== null && measure.effective > today;
                return (
                  <TableRow key={measure.id}>
                    <TableCell className="whitespace-normal">
                      {measureTarget(measure)}
                      <span className="text-xs text-muted-foreground"> · {assets} ativos</span>
                    </TableCell>
                    <TableCell
                      numeric
                      tone={waiting ? "warning" : measure.kind === "SECTOR_EXEMPT" ? "success" : undefined}
                    >
                      {sectorEffect(measure, baseRate, today)}
                    </TableCell>
                    <TableCell numeric variant="note">
                      {waiting
                        ? "aprovada, esperando"
                        : measure.effective
                          ? `desde ${monthYear(measure.effective)}`
                          : ""}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
