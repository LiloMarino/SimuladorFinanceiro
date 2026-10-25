import { useSimulation } from "@/shared/hooks/useSimulation";
import type { IndicatorSettings, StockCandle } from "@/types";
import { StockChart } from "./stock-chart";
import { TechnicalSummary } from "./technical-summary";
import { useStockIndicators } from "../hooks/queries/useStockIndicators";
import { useUpdateIndicatorSettings } from "../hooks/mutations/useUpdateIndicatorSettings";
import { useAnswerCandleChallenge } from "../hooks/mutations/useAnswerCandleChallenge";
import { useCandleChallenge } from "../hooks/queries/useCandleChallenge";
import { useCandlePatterns } from "../hooks/queries/useCandlePatterns";

interface StockAnalysisProps {
  ticker: string;
  history: StockCandle[];
  settings: IndicatorSettings;
}

/** Gráfico e Resumo técnico leem a mesma resposta de indicadores; as dicas de análise técnica ficam com o gráfico. */
export function StockAnalysis({ ticker, history, settings }: StockAnalysisProps) {
  const indicators = useStockIndicators(ticker, settings);
  const updateSettings = useUpdateIndicatorSettings();
  const retry = () => void indicators.refetch();

  // Com a ajuda desligada (Especialista) o gráfico nem pede padrões nem desafio
  const hintsOn = useSimulation().simulation?.simulation?.show_chart_hints ?? true;
  const patterns = useCandlePatterns(ticker, { enabled: hintsOn });
  const challenge = useCandleChallenge(ticker, { enabled: hintsOn });
  const answer = useAnswerCandleChallenge(ticker);

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
        hints={
          hintsOn
            ? {
                patterns: patterns.data,
                patternsStatus: patterns.status,
                onRetryPatterns: () => void patterns.refetch(),
                challenge: challenge.data,
                answering: answer.isPending,
                onAnswer: (direction) => answer.mutate(direction),
              }
            : null
        }
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
