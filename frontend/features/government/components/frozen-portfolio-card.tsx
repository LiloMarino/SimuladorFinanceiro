import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Kpi } from "@/shared/components/kpi";
import { StackedBar } from "@/shared/components/stacked-bar";
import { displayDayMonth, displayMoneyWhole, displayShortDate } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import { shareLabel } from "../lib/government";

// Classes literais para o Tailwind enxergar cada cor
const SLICE_COLORS = [
  "bg-chart-1",
  "bg-chart-2",
  "bg-chart-3",
  "bg-chart-4",
  "bg-chart-5",
  "bg-chart-6",
  "bg-chart-7",
  "bg-chart-8",
] as const;

type FrozenPortfolioCardProps = { panel: GovernmentPanel };

/** A carteira do presidente: congelada até o fim do mandato e pública para a sala. */
export function FrozenPortfolioCard({ panel }: FrozenPortfolioCardProps) {
  const portfolio = panel.portfolio;
  if (!portfolio) return null;
  const colored = portfolio.slices.map((slice, index) => ({
    ...slice,
    color: SLICE_COLORS[index % SLICE_COLORS.length] ?? SLICE_COLORS[0],
  }));

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <h2 className="text-[15px] font-semibold">
            {panel.is_president ? "Sua carteira congelada" : `Carteira congelada de ${portfolio.nickname}`}
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <Kpi
              label="Patrimônio"
              value={displayMoneyWhole(portfolio.total_networth)}
              note="Valoriza ou cai com o mercado, sem você operar."
            />
            <Kpi label="Congelada até" value={displayShortDate(portfolio.frozen_until)} note="O fim do mandato." />
          </div>

          <StackedBar
            segments={colored.map((slice) => ({
              key: slice.label,
              fraction: Number(slice.share),
              color: slice.color,
            }))}
          />

          <ul className="grid">
            {colored.map((slice) => (
              <li key={slice.label} className="flex items-center gap-2.5 py-1.5 text-[13px]">
                <span className={`size-2.5 shrink-0 rounded-[3px] ${slice.color}`} />
                <span className="flex-1">
                  {slice.label}
                  {slice.tickers.length > 0 && (
                    <span className="text-xs text-muted-foreground"> {slice.tickers.join(", ")}</span>
                  )}
                </span>
                <span className="font-mono">{shareLabel(slice.share)}</span>
              </li>
            ))}
          </ul>

          {portfolio.interests.map((interest) => (
            <Alert key={interest.measure_id} variant="warning">
              <TriangleAlert />
              <AlertTitle>
                {interest.sector} é {shareLabel(interest.share)} da{" "}
                {panel.is_president ? "sua carteira" : `carteira de ${portfolio.nickname}`}
              </AlertTitle>
              <AlertDescription>
                {interest.vote_date
                  ? `E a medida do setor está na fila para ${displayDayMonth(interest.vote_date)}.`
                  : interest.effective
                    ? `E a medida do setor vale em ${displayDayMonth(interest.effective)}.`
                    : ""}
              </AlertDescription>
            </Alert>
          ))}

          <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
            {panel.is_president
              ? "Você vence pelo patrimônio, como todos, e não compra nem vende enquanto governa, porque sabe da medida antes da sala."
              : `${portfolio.nickname} vence pelo patrimônio, como todos, mas não compra nem vende enquanto governa, porque sabe da medida antes da sala.`}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
