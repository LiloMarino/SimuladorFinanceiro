import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { MetricLabel } from "@/shared/components/metric-hint";
import { DIVIDENDS_PER_MONTH, TOP_PAYERS } from "@/shared/lib/dividend-metrics";
import { ASSET_CLASS_LABELS } from "@/shared/lib/asset-class";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import type { DividendBucket, PortfolioDividends } from "@/types";
import { usePortfolioDividends } from "../hooks/queries/usePortfolioDividends";
import {
  bucketLabel,
  bucketTitle,
  DIVIDEND_CLASS_COLORS,
  dividendScale,
  payersSentence,
  type DividendPeriod,
} from "../lib/dividend-model";

const PLOT_HEIGHT = 200;

/** Card de proventos da Carteira: o que caiu no caixa por mês ou ano, por classe, e quem pagou. */
export function DividendsCard() {
  const { data, isLoading, error, refetch } = usePortfolioDividends();
  const [period, setPeriod] = useState<DividendPeriod>("month");

  return (
    <Card>
      <CardHeader className="grid-cols-[1fr_auto]">
        <div className="grid gap-1">
          <CardTitle>Proventos nos últimos 12 meses</CardTitle>
          <CardDescription>
            O que caiu no seu caixa em cada mês, por classe de ativo. Passe o mouse num mês para ver quem pagou.
          </CardDescription>
        </div>
        {data && data.payments_count > 0 && (
          <div className="flex items-center gap-4">
            <ClassLegend classes={data.classes} />
            <ToggleGroup
              variant="segmented"
              aria-label="Período das barras"
              value={[period]}
              onValueChange={(values) => values[0] && setPeriod(values[0] as DividendPeriod)}
            >
              <ToggleGroupItem value="month">Por mês</ToggleGroupItem>
              <ToggleGroupItem value="year">Por ano</ToggleGroupItem>
            </ToggleGroup>
          </div>
        )}
      </CardHeader>
      <CardContent>
        {isLoading && <Skeleton className="h-56" />}
        {!isLoading && !data && (
          <ErrorState
            title="Não deu pra carregar os proventos"
            description="Os proventos já recebidos continuam no caixa. Tente de novo."
            error={error}
            onRetry={() => void refetch()}
          />
        )}
        {data && data.payments_count === 0 && (
          <p className="py-10 text-center text-[13px] text-muted-foreground">
            Nenhum provento recebido ainda. Ações e fundos imobiliários pagam direto no caixa, na data ex, pela
            quantidade que você tinha na abertura do dia.
          </p>
        )}
        {data && data.payments_count > 0 && <DividendsBody data={data} period={period} />}
      </CardContent>
    </Card>
  );
}

function ClassLegend({ classes }: { classes: PortfolioDividends["classes"] }) {
  return (
    <ul className="flex gap-3.5 text-xs text-muted-foreground">
      {classes.map((assetClass) => (
        <li key={assetClass} className="flex items-center gap-1.5">
          {ASSET_CLASS_LABELS[assetClass]}
          <span className={cn("size-2.5 rounded-[3px]", DIVIDEND_CLASS_COLORS[assetClass])} aria-hidden="true" />
        </li>
      ))}
    </ul>
  );
}

function DividendsBody({ data, period }: { data: PortfolioDividends; period: DividendPeriod }) {
  const buckets = period === "month" ? data.monthly : data.yearly;

  return (
    <div className="grid gap-8 lg:grid-cols-[200px_minmax(0,1fr)_380px]">
      <div className="grid content-start gap-4">
        <div className="grid gap-0.5">
          <span className="text-xs font-medium text-muted-foreground">Recebido em 12 meses</span>
          <b className="font-mono text-[22px]">{displayMoney(data.total_12m)}</b>
          <span className="text-xs text-faint-foreground">
            {data.payments_count} {data.payments_count === 1 ? "pagamento" : "pagamentos"} na partida
            {data.first_payment_date && `, desde ${displayShortMonthYear(data.first_payment_date)}`}
          </span>
        </div>
        <div className="grid gap-0.5">
          <span className="text-xs font-medium text-muted-foreground">
            <MetricLabel metric={DIVIDENDS_PER_MONTH} />
          </span>
          <b className="font-mono text-[22px]">{displayMoney(data.average_per_month)}</b>
          <span className="text-xs text-faint-foreground">contando os meses sem provento</span>
        </div>
      </div>

      <DividendBars buckets={buckets} period={period} />

      <TopPayers payers={data.payers} />
    </div>
  );
}

function DividendBars({ buckets, period }: { buckets: DividendBucket[]; period: DividendPeriod }) {
  const [active, setActive] = useState<number | null>(null);
  const { ceiling, ticks } = dividendScale(Math.max(0, ...buckets.map((b) => Number(b.amount))));
  const hovered = active === null ? undefined : buckets[active];

  return (
    <div className="relative h-[226px]" onPointerLeave={() => setActive(null)}>
      {/* Eixo e linhas de grade */}
      <div className="absolute inset-x-0 top-0 bottom-[26px]">
        {ticks.map((tick) => (
          <div
            key={tick}
            className="absolute inset-x-0 flex translate-y-1/2 items-center"
            style={{ bottom: `${(tick / ceiling) * PLOT_HEIGHT}px` }}
          >
            <span className="w-12 pr-2 text-right font-mono text-xs text-faint-foreground">
              {tick === 0 ? "0" : displayMoney(tick).replace(",00", "")}
            </span>
            <i className={cn("flex-1 border-t", tick === 0 ? "border-input" : "border-border/60")} />
          </div>
        ))}
      </div>

      {/* Barras empilhadas por classe */}
      <div
        className="absolute inset-y-0 right-0 left-14 grid justify-items-center"
        style={{ gridTemplateColumns: `repeat(${buckets.length}, 1fr)` }}
      >
        {buckets.map((bucket, index) => (
          <button
            key={bucket.period}
            type="button"
            aria-label={`${bucketTitle(bucket, period)}: ${displayMoney(bucket.amount)}`}
            className="flex h-full w-full cursor-default flex-col items-center justify-end gap-2 outline-none"
            onPointerEnter={() => setActive(index)}
            onFocus={() => setActive(index)}
            onBlur={() => setActive(null)}
          >
            <div className="flex w-[34px] max-w-full flex-col-reverse" style={{ height: `${PLOT_HEIGHT}px` }}>
              {bucket.by_class.map((part) => (
                <i
                  key={part.asset_class}
                  className={cn(
                    "block first:rounded-b-[3px] last:rounded-t-[3px]",
                    DIVIDEND_CLASS_COLORS[part.asset_class],
                    active === index && "brightness-95",
                  )}
                  style={{ height: `${(Number(part.amount) / ceiling) * PLOT_HEIGHT}px`, flexShrink: 0 }}
                />
              ))}
            </div>
            <span className="h-[18px] text-xs text-faint-foreground">{bucketLabel(bucket, period)}</span>
          </button>
        ))}
      </div>

      {hovered && active !== null && (
        <BarTooltip bucket={hovered} period={period} index={active} count={buckets.length} />
      )}
    </div>
  );
}

/** O tooltip passa para a esquerda da barra na metade final, para não sair do card. */
function BarTooltip({
  bucket,
  period,
  index,
  count,
}: {
  bucket: DividendBucket;
  period: DividendPeriod;
  index: number;
  count: number;
}) {
  const center = `calc(56px + (100% - 56px) * ${(index + 0.5) / count})`;
  const onLeft = index >= count / 2;

  return (
    <div
      role="tooltip"
      className="pointer-events-none absolute bottom-20 z-10 w-[220px] rounded-[10px] bg-foreground px-3.5 py-3 text-xs leading-normal text-background shadow-lg"
      style={onLeft ? { left: `calc(${center} - 220px - 24px)` } : { left: `calc(${center} + 24px)` }}
    >
      <b>
        {bucketTitle(bucket, period)} · <span className="font-mono">{displayMoney(bucket.amount)}</span>
      </b>
      <div className="mt-1.5 grid gap-0.5">
        {bucket.by_class.map((part) => (
          <div key={part.asset_class} className="flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              {ASSET_CLASS_LABELS[part.asset_class]}
              <span className={cn("size-2.5 rounded-[3px]", DIVIDEND_CLASS_COLORS[part.asset_class])} />
            </span>
            <b className="font-mono">{displayMoney(part.amount)}</b>
          </div>
        ))}
      </div>
      <div className="mt-1 opacity-70">{payersSentence(bucket, period)}</div>
    </div>
  );
}

function TopPayers({ payers }: { payers: PortfolioDividends["payers"] }) {
  const leader = payers[0];

  return (
    <div className="grid content-start gap-3 lg:border-l lg:pl-7">
      <div className="grid gap-0.5">
        <span className="text-xs font-medium text-muted-foreground">
          <MetricLabel metric={TOP_PAYERS} />
        </span>
        {leader && (
          <span className="text-xs text-faint-foreground">
            A parte de cada ativo no total: {leader.ticker} trouxe {displayPercent(leader.share, 0)} de tudo o que
            entrou.
          </span>
        )}
      </div>
      {payers.length === 0 && (
        <span className="text-[13px] text-muted-foreground">Nenhum ativo pagou nos últimos 12 meses.</span>
      )}
      {payers.map((payer) => (
        <div key={payer.ticker} className="grid grid-cols-[64px_1fr_92px_36px] items-center gap-2.5 text-[13px]">
          <b>{payer.ticker}</b>
          <div className="h-2 rounded bg-muted">
            <i
              className={cn("block h-2 rounded", DIVIDEND_CLASS_COLORS[payer.asset_class])}
              style={{ width: `${Number(payer.share) * 100}%` }}
            />
          </div>
          <span className="text-right font-mono">{displayMoney(payer.amount)}</span>
          <span className="text-right font-mono text-xs text-faint-foreground">{displayPercent(payer.share, 0)}</span>
        </div>
      ))}
    </div>
  );
}
