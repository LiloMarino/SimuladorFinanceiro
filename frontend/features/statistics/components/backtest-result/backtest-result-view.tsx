import { Link } from "react-router-dom";
import { ErrorState } from "@/shared/components/error-state";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useBacktestResult } from "@/shared/hooks/queries/useBacktestResult";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { StatisticsReport } from "../statistics-report";
import { BacktestHeader } from "./backtest-header";
import { BacktestOverviewTab } from "./backtest-overview";

/** O fechamento de um backtest: o cabeçalho com o período e as regras, e o relatório com o Geral próprio. */
export function BacktestResultView({ simulationId }: { simulationId: number }) {
  const { data: result, error, refetch } = useBacktestResult(simulationId);
  const { data: settings } = useSimulationSettings();

  if (error && !result) {
    return (
      <Card>
        <CardContent>
          <ErrorState
            title="Não conseguimos carregar o backtest"
            description="Ele está salvo. Tente de novo ou volte ao lobby: o resultado fica em “Simulações salvas”."
            error={error}
            onRetry={() => void refetch()}
          >
            <Button variant="outline" nativeButton={false} render={<Link to="/lobby" />}>
              Voltar ao lobby
            </Button>
          </ErrorState>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-5">
      {result ? (
        <BacktestHeader simulationId={simulationId} result={result} isHost={settings?.is_host ?? false} />
      ) : (
        <Skeleton className="h-20" />
      )}

      {/* Relatório do backtest: as abas das Estatísticas, com o Geral de estratégias */}
      <StatisticsReport title="Relatório do backtest" simulationIds={[simulationId]} overview={BacktestOverviewTab} />
    </div>
  );
}
