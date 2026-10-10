import { Fragment } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ChartEmptyCard } from "@/features/portfolio/components/shared/chart-empty-card";
import { stringToColor } from "@/shared/lib/utils";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { SectorAllocation } from "@/types";

const UNCLASSIFIED = "Sem setor";
const TITLE = "Renda Variável por Setor";

interface SectorAllocationCardProps {
  sectors: SectorAllocation[];
}

export function SectorAllocationCard({ sectors }: SectorAllocationCardProps) {
  if (!sectors.length) {
    return <ChartEmptyCard title={TITLE} height={200} message="Nenhuma ação na carteira" />;
  }

  const chartData = sectors.map((s) => ({ name: s.sector ?? UNCLASSIFIED, fraction: Number(s.fraction) }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{TITLE}</CardTitle>
        <CardDescription>
          Quanto da renda variável está em cada setor. A classificação se edita na Central de dados.
        </CardDescription>
      </CardHeader>

      <CardContent className="grid gap-6 lg:grid-cols-2">
        {/* Barras por setor */}
        <ResponsiveContainer width="100%" height={Math.max(160, chartData.length * 40)}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
            <XAxis type="number" domain={[0, 1]} tickFormatter={(v: number) => displayPercent(v, 0)} />
            <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(v: number) => displayPercent(v)}
              labelClassName="font-medium"
              cursor={{ fillOpacity: 0.1 }}
            />
            <Bar dataKey="fraction" name="Fração" radius={[0, 4, 4, 0]}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={stringToColor(entry.name)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Tabela por setor e segmento */}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Setor / Segmento</TableHead>
              <TableHead className="text-right">Valor</TableHead>
              <TableHead className="text-right">% da renda variável</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sectors.map((sector) => (
              <Fragment key={sector.sector ?? UNCLASSIFIED}>
                <TableRow className="font-medium">
                  <TableCell>{sector.sector ?? UNCLASSIFIED}</TableCell>
                  <TableCell className="text-right">{displayMoney(sector.value)}</TableCell>
                  <TableCell className="text-right">{displayPercent(sector.fraction)}</TableCell>
                </TableRow>
                {sector.sector &&
                  sector.segments.map((segment) => (
                    <TableRow key={segment.segment} className="text-muted-foreground">
                      <TableCell className="pl-6">{segment.segment}</TableCell>
                      <TableCell className="text-right">{displayMoney(segment.value)}</TableCell>
                      <TableCell className="text-right">{displayPercent(segment.fraction)}</TableCell>
                    </TableRow>
                  ))}
              </Fragment>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
