import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { Position } from "@/types";

/** A posição do jogador no ativo, com o que está preso em ordens abertas. */
export function PositionCard({ ticker, position }: { ticker: string; position: Position | null }) {
  const held = position && position.size > 0 ? position : null;
  const positive = held ? Number(held.return_value) >= 0 : true;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sua posição</CardTitle>
      </CardHeader>
      <CardContent>
        {!held ? (
          <p className="text-[13px] text-muted-foreground">Nenhuma ação de {ticker}.</p>
        ) : (
          <dl className="grid grid-cols-2 gap-4">
            <div className="grid gap-0.5">
              <dt className="text-xs text-muted-foreground">Quantidade</dt>
              <dd className="font-mono font-semibold">
                {held.size}
                {held.reserved > 0 && (
                  <span className="font-sans text-xs font-normal text-muted-foreground">
                    {" "}
                    · {held.reserved} em ordens
                  </span>
                )}
              </dd>
            </div>
            <div className="grid gap-0.5">
              <dt className="text-xs text-muted-foreground">Preço médio</dt>
              <dd className="font-mono font-semibold">{displayMoney(held.avg_price)}</dd>
            </div>
            <div className="grid gap-0.5">
              <dt className="text-xs text-muted-foreground">Valor hoje</dt>
              <dd className="font-mono font-semibold">{displayMoney(held.current_value)}</dd>
            </div>
            <div className="grid gap-0.5">
              <dt className="text-xs text-muted-foreground">Resultado</dt>
              <dd
                className={
                  positive ? "font-mono font-semibold text-success" : "font-mono font-semibold text-destructive"
                }
              >
                {positive ? "+" : ""}
                {displayMoney(held.return_value)} · {displayPercent(held.return_pct)}
              </dd>
            </div>
          </dl>
        )}
      </CardContent>
    </Card>
  );
}
