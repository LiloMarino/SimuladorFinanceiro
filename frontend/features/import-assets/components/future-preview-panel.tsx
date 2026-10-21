import type { UseQueryResult } from "@tanstack/react-query";
import { Badge } from "@/shared/components/ui/badge";
import { ErrorState } from "@/shared/components/error-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { displayNumber } from "@/shared/lib/utils/display";
import type { FuturePreview } from "@/types";
import { PreviewChart } from "./preview-chart";
import { PreviewNumbers } from "./preview-numbers";

const IBOV_TAB = "IBOV";

type FuturePreviewPanelProps = {
  query: UseQueryResult<FuturePreview>;
  /** Os primeiros ativos da cobertura, que viram abas ao lado do Ibovespa */
  tickers: string[];
  /** Ativo mostrado no gráfico; nulo é o Ibovespa */
  ticker: string | null;
  onTickerChange: (ticker: string | null) => void;
};

const assetValue = (value: number) => displayNumber(value, Math.abs(value) >= 100 ? 0 : 2);

function PreviewSkeleton() {
  return (
    <div className="grid gap-3.5">
      <Skeleton className="h-45" />
      <div className="grid grid-cols-2 gap-2">
        {Array.from({ length: 4 }, (_, i) => (
          <Skeleton key={i} className="h-14.5" />
        ))}
      </div>
      <span className="text-xs text-muted-foreground">
        Só na primeira vez: depois, cada mudança de controle refaz a prévia num instante.
      </span>
    </div>
  );
}

/** A prévia do futuro: curva real × gerada, os quatro números e os indicadores, sem gravar nada. */
export function FuturePreviewPanel({ query, tickers, ticker, onTickerChange }: FuturePreviewPanelProps) {
  const { data: preview, isError, error, isFetching, isPlaceholderData } = query;

  const status = isFetching && (
    <span className="inline-flex items-center gap-1.5 text-xs font-normal text-muted-foreground">
      <Spinner className="size-3.5" />
      {preview ? "Atualizando…" : "Lendo o histórico…"}
    </span>
  );

  const renderBody = () => {
    if (isError) {
      return (
        <ErrorState
          title="Não deu pra montar a prévia"
          description={
            error.status === 400 ? error.message : "Confira se o servidor do host está ligado. Os controles continuam valendo."
          }
          error={error}
          onRetry={() => void query.refetch()}
        />
      );
    }
    if (!preview) return <PreviewSkeleton />;

    // Ao trocar de ativo, a prévia anterior ainda não traz a curva do novo
    const series = ticker === null ? preview.ibov : preview.asset?.key === ticker ? preview.asset : null;

    return (
      <div className={cn("grid gap-3.5 transition-opacity", isPlaceholderData && "opacity-45")}>
        <div className="grid gap-1.5">
          <div className="flex items-baseline justify-between">
            <span className="text-xs font-medium text-muted-foreground">
              {ticker === null ? "Ibovespa · pontos" : `${ticker} · R$`}
            </span>
            <div className="flex items-center gap-3.5 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="h-0.75 w-4 rounded-full bg-chart-1" />
                Real
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-0.75 w-4 rounded-full bg-chart-3" />
                Gerado
              </span>
            </div>
          </div>
          {series ? (
            <PreviewChart
              series={series}
              height={220}
              maxYearTicks={7}
              formatValue={ticker === null ? (v) => `${Math.round(v / 1000)}k` : assetValue}
              formatTooltip={ticker === null ? (v) => displayNumber(v, 0) : (v) => displayNumber(v, 2)}
            />
          ) : (
            <Skeleton className="h-55" />
          )}
        </div>

        <PreviewNumbers preview={preview} />

        <div className="grid grid-cols-1 gap-4 min-[1100px]:grid-cols-2">
          <div className="grid gap-1">
            <span className="text-xs font-medium text-muted-foreground">SELIC · % ao ano</span>
            <PreviewChart
              series={preview.selic}
              height={120}
              maxYearTicks={4}
              formatValue={(v) => `${displayNumber(v, 0)}%`}
              formatTooltip={(v) => `${displayNumber(v, 2)}% ao ano`}
            />
          </div>
          <div className="grid gap-1">
            <span className="text-xs font-medium text-muted-foreground">Inflação · IPCA de 12 meses</span>
            <PreviewChart
              series={preview.ipca_12m}
              height={120}
              maxYearTicks={4}
              formatValue={(v) => `${displayNumber(v, 0)}%`}
              formatTooltip={(v) => `${displayNumber(v, 2)}%`}
            />
          </div>
        </div>

        <span className="text-xs text-muted-foreground">
          Um futuro entre muitos: outra semente dá outro, igualmente plausível.
        </span>
      </div>
    );
  };

  return (
    <section className="grid gap-3.5">
      {/* Cabeçalho da prévia */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <h3 className="text-[15px] font-semibold">Prévia</h3>
          <Badge variant="secondary">não grava nada</Badge>
          {status}
        </div>
        <ToggleGroup
          variant="segmented"
          aria-label="Série mostrada na prévia"
          value={[ticker ?? IBOV_TAB]}
          onValueChange={(values) => values[0] && onTickerChange(values[0] === IBOV_TAB ? null : values[0])}
        >
          <ToggleGroupItem value={IBOV_TAB}>Ibovespa</ToggleGroupItem>
          {tickers.map((key) => (
            <ToggleGroupItem key={key} value={key}>
              {key}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      {renderBody()}
    </section>
  );
}
