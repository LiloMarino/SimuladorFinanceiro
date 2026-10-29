import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import type { EconomyPanel } from "@/types";
import { economyRows } from "../lib/economy";
import { SeriesChart } from "./series-chart";

type UnemploymentCardProps = { panel: EconomyPanel };

/** O desemprego ao longo da partida, com a regra que o liga ao crescimento. */
export function UnemploymentCard({ panel }: UnemploymentCardProps) {
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

          <p className="rounded-md bg-subtle px-2.5 py-1.5 text-xs text-muted-foreground">
            Segue o crescimento: cada ponto acima da tendência baixa o desemprego em cerca de meio ponto em um ano. Ex.:
            crescendo 3% contra os 2% da tendência, o desemprego cai uns 0,5 ponto em 12 meses.
          </p>
          <span className="text-[12.5px] text-muted-foreground">
            Pesa para quem tem carteira assinada e para quem depende de auxílio.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
