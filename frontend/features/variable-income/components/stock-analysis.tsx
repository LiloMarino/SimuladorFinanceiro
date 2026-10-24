import type { IndicatorSettings, StockCandle } from "@/types";
import { StockChart } from "./stock-chart";
import { TechnicalSummary } from "./technical-summary";
import { useStockIndicators } from "../hooks/queries/useStockIndicators";
import { useUpdateIndicatorSettings } from "../hooks/mutations/useUpdateIndicatorSettings";

interface StockAnalysisProps {
  ticker: string;
  history: StockCandle[];
  settings: IndicatorSettings;
}

/** Gráfico e Resumo técnico leem a mesma resposta de indicadores. */
export function StockAnalysis({ ticker, history, settings }: StockAnalysisProps) {
  const indicators = useStockIndicators(ticker, settings);
  const updateSettings = useUpdateIndicatorSettings();
  const retry = () => void indicators.refetch();

  return (
    <>
      <StockChart
        ticker={ticker}
        initialData={history}
        settings={settings}
        indicators={indicators.data}
        indicatorsStatus={indicators.status}
        onRetryIndicators={retry}
        onSettingsChange={(next) => updateSettings.mutate(next)}
      />
      <TechnicalSummary
        summary={indicators.data?.summary}
        params={settings.params}
        status={indicators.status}
        onRetry={retry}
      />
    </>
  );
}
