import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import { cn } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import { economyRows } from "../lib/economy";
import { signedPoints } from "../lib/economy-metrics";
import { SeriesChart } from "./series-chart";

type UnemploymentCardProps = { panel: EconomyPanel };

/** O desemprego ao longo da partida e, com o governo, a história mais o que a partida somou. */
export function UnemploymentCard({ panel }: UnemploymentCardProps) {
  const { growth_parts: parts } = panel;
  const added = Number(parts.unemployment) - Number(parts.history_unemployment);

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3">
          <div className="flex items-center gap-1.5">
            <h2 className="text-[15px] font-semibold">{UNEMPLOYMENT.label}</h2>
            <InfoHint label="Como ler o desemprego">
              <div className="space-y-1 text-left">
                <p>{UNEMPLOYMENT.definition}</p>
                <p>{UNEMPLOYMENT.example}</p>
                <p>{UNEMPLOYMENT.reading}</p>
              </div>
            </InfoHint>
          </div>

          <SeriesChart rows={economyRows(panel)} dataKey="unemployment" label="Desemprego" color="var(--chart-4)" />

          {/* De onde vem o desemprego de hoje */}
          {panel.links !== null && (
            <div className="grid gap-1.5 text-[13px]">
              <div className="flex items-center justify-between gap-4">
                <span>Desemprego da história</span>
                <span className="font-mono font-semibold">{displayPercent(parts.history_unemployment, 1)}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>O que a partida somou</span>
                <span
                  className={cn(
                    "font-mono font-semibold",
                    Math.abs(added) < 0.0005 ? "text-foreground" : added > 0 ? "text-destructive" : "text-success",
                  )}
                >
                  {signedPoints(added)} ponto{Math.abs(added) >= 0.0195 ? "s" : ""}
                </span>
              </div>
              <div className="flex items-center justify-between gap-4 border-t pt-1.5">
                <span className="font-medium">Desemprego hoje</span>
                <span className="font-mono font-semibold">{displayPercent(parts.unemployment, 1)}</span>
              </div>
            </div>
          )}

          <p className="rounded-md bg-subtle px-2.5 py-1.5 text-xs text-muted-foreground">
            A história é a taxa de desocupação da PNAD Contínua do IBGE. Com a expansão Governo, o desemprego segue o
            crescimento a mais: cada ponto de crescimento acima da história baixa o desemprego em cerca de meio ponto em
            um ano. Ex.: crescendo 3% contra os 2% da história, o desemprego fica uns 0,5 ponto abaixo do da história em
            12 meses.
          </p>
          <span className="text-[12.5px] text-muted-foreground">
            Pesa para quem tem carteira assinada e para quem depende de auxílio.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
