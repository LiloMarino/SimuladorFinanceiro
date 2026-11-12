import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useEconomyPanel } from "@/shared/hooks/queries/useEconomyPanel";
import { GDP } from "@/shared/lib/budget-metrics";
import { displayMoneyLarge, displayPercent, displaySignedPercent } from "@/shared/lib/utils/display";
import { growthTone, type GrowthTone } from "../lib/country";

const GROWTH_BADGE: Record<GrowthTone, "success" | "secondary" | "destructive"> = {
  good: "success",
  weak: "secondary",
  recession: "destructive",
};

/** Faixa "O país" no pé do cabeçalho: o tamanho da economia, o ritmo dela e o peso da dívida, em todas as abas. */
export function CountryStrip() {
  const { data: economy } = useEconomyPanel();
  const debt = economy?.debt;
  const last = economy?.points.at(-1);

  // Sem a expansão Governo a economia não traz PIB nem dívida: a faixa não existe
  if (economy && (!debt || !last)) return null;

  return (
    <div className="-mx-(--card-spacing) -mb-(--card-spacing) mt-4 flex flex-wrap items-center gap-x-8 gap-y-2 border-t bg-subtle px-(--card-spacing) py-3 text-[13px]">
      <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">O país</span>
      {debt && last ? (
        <>
          <span className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
            <span className="inline-flex items-center gap-1 text-muted-foreground">
              {GDP.label}
              <MetricHint metric={GDP} />
            </span>
            <b className="font-mono">{displayMoneyLarge(debt.gdp)} por ano</b>
            <Badge variant={GROWTH_BADGE[growthTone(Number(last.growth))]} size="sm" numeric>
              {displaySignedPercent(last.growth, 1)} em 12 meses
            </Badge>
          </span>
          <span className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
            <span className="text-muted-foreground">Dívida</span>
            <b className="font-mono">
              {displayMoneyLarge(debt.debt_amount)} · {displayPercent(debt.debt, 1)} do PIB
            </b>
          </span>
        </>
      ) : (
        <Skeleton className="h-5 w-96 max-w-full" />
      )}
    </div>
  );
}
