import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { InfoHint } from "@/shared/components/info-hint";
import { Kpi } from "@/shared/components/kpi";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { MARK_TO_MARKET, YIELDED } from "@/shared/lib/treasury-metrics";
import type { TreasuryPosition } from "@/types";
import { useTreasuryCover } from "../hooks/queries/useTreasuryCover";
import { useSetTreasuryCover } from "../hooks/mutations/useSetTreasuryCover";
import { displayDay, displayGain, indexDotClass, treasuryMoney, treasuryRateLabel } from "../lib/treasury";

const COLUMNS = 8;

const sum = (positions: TreasuryPosition[], field: "total_applied" | "mark" | "market_value") =>
  positions.reduce((total, position) => total + Number(position[field]), 0);

const markTone = (value: number) => (value > 0 ? "success" : value < 0 ? "destructive" : undefined);

type HoldingsCardProps = {
  positions: TreasuryPosition[];
  onSell: (position: TreasuryPosition) => void;
};

/** Os títulos do Tesouro do jogador: totais, a chave da cobertura automática e uma linha por posição. */
export function HoldingsCard({ positions, onSell }: HoldingsCardProps) {
  const { data: cover } = useTreasuryCover();
  const setCover = useSetTreasuryCover();
  const mark = sum(positions, "mark");

  return (
    <Card className="overflow-hidden">
      {/* Cabeçalho */}
      <CardHeader>
        <CardTitle>Seus títulos do Tesouro</CardTitle>
        <CardDescription>
          Dá para vender em qualquer dia, inteiro ou em parte, pelo preço de hoje. Se a taxa subiu desde a sua compra, o
          título vale menos que a curva; se caiu, vale mais.
        </CardDescription>
        <CardAction>
          <div className="flex gap-6">
            <Kpi size="sm" label="Aplicado" value={treasuryMoney(sum(positions, "total_applied"))} />
            <Kpi
              size="sm"
              label={
                <>
                  Marcação <MetricHint metric={MARK_TO_MARKET} />
                </>
              }
              value={displayGain(mark)}
              tone={markTone(mark)}
            />
            <Kpi size="sm" label="Vale hoje" value={treasuryMoney(sum(positions, "market_value"))} />
          </div>
        </CardAction>
      </CardHeader>

      {/* Cobertura automática */}
      <CardContent>
        <div className="flex h-10 w-fit items-center gap-2 rounded-lg border border-input px-3">
          <Switch
            id="treasury-cover"
            checked={cover?.enabled ?? false}
            disabled={cover === undefined || setCover.isPending}
            onCheckedChange={(enabled) => setCover.mutate({ enabled })}
          />
          <Label htmlFor="treasury-cover">Cobrir despesas também com Prefixado e IPCA+</Label>
          <InfoHint label="Como funciona a cobertura">
            Sem caixa, a despesa vende sozinha a liquidez diária e o Tesouro Selic. Ligada, vende também o Prefixado e o
            IPCA+, a preço de mercado, e pode realizar perda de marcação.
          </InfoHint>
        </div>
      </CardContent>

      {/* Listagem */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Título</TableHead>
            <TableHead numeric>Comprou a</TableHead>
            <TableHead numeric>
              <MetricLabel metric={YIELDED} />
            </TableHead>
            <TableHead numeric>Hoje paga</TableHead>
            <TableHead numeric>Aplicado</TableHead>
            <TableHead numeric>
              <MetricLabel metric={MARK_TO_MARKET} />
            </TableHead>
            <TableHead numeric>Vale hoje</TableHead>
            <TableHead>
              <span className="sr-only">Vender</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {positions.length === 0 && (
            <TableEmptyRow colSpan={COLUMNS}>
              <Empty>
                <EmptyHeader>
                  <EmptyTitle>Você ainda não tem título do Tesouro</EmptyTitle>
                </EmptyHeader>
              </Empty>
            </TableEmptyRow>
          )}
          {positions.map((position) => {
            const { asset } = position;
            const positionMark = Number(position.mark);
            return (
              <TableRow key={asset.asset_uuid}>
                <TableCell>
                  <div className="grid gap-0.5">
                    <span className="flex items-center gap-2 font-semibold">
                      <span aria-hidden className={cn("size-2.5 rounded-full", indexDotClass(asset.rate_index))} />
                      {asset.name}
                    </span>
                    <span className="pl-[18px] text-xs text-muted-foreground">
                      comprado em {displayDay(position.first_applied_date)}
                    </span>
                  </div>
                </TableCell>
                <TableCell numeric>{treasuryRateLabel(asset.rate_index, position.bought_rate)}</TableCell>
                <TableCell numeric tone="success">
                  {displayGain(position.yield_amount)}
                </TableCell>
                <TableCell numeric>{treasuryRateLabel(asset.rate_index, position.today_rate)}</TableCell>
                <TableCell numeric>{treasuryMoney(position.total_applied)}</TableCell>
                <TableCell numeric>
                  {asset.rate_index === "SELIC" ? (
                    <div className="grid gap-0.5">
                      <span>—</span>
                      <span className="font-sans text-xs font-normal text-muted-foreground">vale o acumulado</span>
                    </div>
                  ) : (
                    <span className={cn(positionMark > 0 && "text-success", positionMark < 0 && "text-destructive")}>
                      {displayGain(position.mark)}
                    </span>
                  )}
                </TableCell>
                <TableCell numeric>
                  <span className="font-semibold">{treasuryMoney(position.market_value)}</span>
                </TableCell>
                <TableCell>
                  <Button variant="outline" size="sm" onClick={() => onSell(position)}>
                    Vender
                  </Button>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
