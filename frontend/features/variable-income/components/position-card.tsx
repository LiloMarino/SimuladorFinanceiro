import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { MetricLabel } from "@/shared/components/metric-hint";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { YIELD_ON_COST } from "@/shared/lib/dividend-metrics";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { Position } from "@/types";
import { useCorporateEvents } from "../hooks/queries/useCorporateEvents";

/** A posição da conta ativa (a do jogador ou a da gestora) no ativo, com o que está preso em ordens abertas. */
export function PositionCard({ ticker, position }: { ticker: string; position: Position | null }) {
  const held = position && Number(position.size) > 0 ? position : null;
  const positive = held ? Number(held.return_value) >= 0 : true;
  const { data: events } = useCorporateEvents(ticker);
  const { fund } = useActiveAccount();

  return (
    <Card>
      <CardHeader>
        <CardTitle>{fund ? `Posição da ${fund.name}` : "Sua posição"}</CardTitle>
        {fund && (
          <Badge variant="info" size="tag" className="justify-self-start">
            conta: {fund.name}
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        {!held ? (
          <p className="text-[13px] text-muted-foreground">
            {fund ? `A ${fund.name} não tem ${ticker}.` : `Você não tem ${ticker}.`}
          </p>
        ) : (
          <dl>
            <PositionRow label="Quantidade">
              {displayQuantity(held.size)}
              {Number(held.reserved) > 0 && (
                <span className="font-sans text-xs font-normal text-muted-foreground">
                  {" "}
                  · {displayQuantity(held.reserved)} em ordens
                </span>
              )}
            </PositionRow>
            <PositionRow label="Resultado" className={positive ? "text-success" : "text-destructive"}>
              {positive ? "+" : ""}
              {displayMoney(held.return_value)}{" "}
              <span className="text-xs">
                {positive ? "▲" : "▼"} {displayPercent(Math.abs(Number(held.return_pct)))}
              </span>
            </PositionRow>
            {/* Proventos da posição: o resultado acima é só preço */}
            {events && (
              <div className="-mx-(--card-spacing) mt-2 bg-warning-soft px-(--card-spacing) py-1">
                <PositionRow
                  label={
                    <span className="inline-flex items-center gap-1.5">
                      Proventos recebidos
                      <span className="size-2.5 rounded-[3px] bg-dividend-bar" aria-hidden="true" />
                    </span>
                  }
                >
                  {displayMoney(events.received_total)}
                </PositionRow>
                <PositionRow label={<MetricLabel metric={YIELD_ON_COST} />} last>
                  {events.yield_on_cost === null ? "—" : displayPercent(events.yield_on_cost, 1)}
                  {events.dividend_yield_12m !== null && (
                    <span className="font-sans text-xs font-normal text-faint-foreground">
                      {" "}
                      DY {displayPercent(events.dividend_yield_12m, 1)}
                    </span>
                  )}
                </PositionRow>
              </div>
            )}
            <PositionRow label="Preço médio">{displayMoney(held.avg_price)}</PositionRow>
            <PositionRow label="Valor hoje" last>
              {displayMoney(held.current_value)}
            </PositionRow>
          </dl>
        )}
      </CardContent>
    </Card>
  );
}

/** Uma linha rótulo/valor da lista, com divisória embaixo (menos na última). */
function PositionRow({
  label,
  children,
  className,
  last = false,
}: {
  label: ReactNode;
  children: ReactNode;
  className?: string;
  last?: boolean;
}) {
  return (
    <div className={cn("flex items-center justify-between py-2 text-[13px]", !last && "border-b border-muted")}>
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={cn("font-mono font-semibold", className)}>{children}</dd>
    </div>
  );
}
