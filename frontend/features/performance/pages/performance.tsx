import { useState } from "react";
import { CircleAlert } from "lucide-react";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useDebugStatus } from "@/shared/hooks/queries/useDebugMode";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import type ApiError from "@/shared/lib/models/ApiError";
import { ErrorState } from "@/shared/components/error-state";
import { displayDuration } from "@/shared/lib/utils/display";
import { ControlsBar } from "../components/controls-bar";
import { KpiCards } from "../components/kpi-cards";
import { PySpyCard } from "../components/pyspy-card";
import { PerformanceDebugOff, PerformanceEmpty, PerformanceHostOnly, PerformanceLoading } from "../components/states";
import { TimeTable } from "../components/time-table";
import { TrafficTable } from "../components/traffic-table";
import { useMetrics } from "../hooks/queries/useMetrics";
import { useResetMetrics } from "../hooks/mutations/useResetMetrics";
import { buildRows, engineStatus, sortRows } from "../lib/stats";

const TABLE_ID = "tabela-tempo";

/** Falha de leitura sem nada para mostrar (as medições ou o modo debug). */
function ReadFailure({ error, onRetry }: { error: ApiError | null; onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <ErrorState
          title="Não deu para ler as medições"
          description="O servidor não respondeu. A coleta continua rodando; só a leitura falhou. Se repetir, o motivo fica em logs/error.log."
          error={error}
          onRetry={onRetry}
        />
      </CardContent>
    </Card>
  );
}

export default function PerformancePage() {
  usePageLabel("Desempenho");
  const { debug, isPending: debugPending, error: debugError, refetch: refetchDebug } = useDebugStatus();
  const [paused, setPaused] = useState(false);
  const { data, error, isPending, refetch, dataUpdatedAt } = useMetrics({
    paused,
    enabled: debug,
  });
  const reset = useResetMetrics();

  if (debugPending || (debug && isPending)) return <PerformanceLoading />;
  if (debugError) {
    return <ReadFailure error={debugError} onRetry={() => void refetchDebug()} />;
  }
  if (!debug) return <PerformanceDebugOff />;
  if (error?.status === 403) return <PerformanceHostOnly />;
  if (!data) {
    return <ReadFailure error={error} onRetry={() => void refetch()} />;
  }

  const rows = buildRows(data.items);
  const rowsByTotal = sortRows(rows, "total_ms");
  const engine = engineStatus(data);
  const empty = data.items.length === 0 && data.traffic.length === 0;

  return (
    <div className="grid gap-5">
      <ControlsBar
        paused={paused}
        failed={!!error}
        updatedAt={dataUpdatedAt}
        resetting={reset.isPending}
        onTogglePause={() => setPaused((value) => !value)}
        onReset={() => reset.mutate()}
      />

      {/* Falha depois de já haver dados: os números na tela são da última leitura */}
      {error && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertTitle>Não deu para atualizar as medições</AlertTitle>
          <AlertDescription>
            Os números abaixo são da última leitura que deu certo, às{" "}
            {new Date(dataUpdatedAt).toLocaleTimeString("pt-BR")}.
          </AlertDescription>
          <AlertAction>
            <Button variant="outline" size="sm" onClick={() => void refetch()}>
              Tentar de novo
            </Button>
          </AlertAction>
        </Alert>
      )}

      {empty ? (
        <PerformanceEmpty />
      ) : (
        <>
          {engine.late && engine.item && engine.budgetMs !== null && (
            <Alert variant="destructive">
              <CircleAlert />
              <AlertTitle>O tempo está andando mais devagar que o pedido</AlertTitle>
              <AlertDescription>
                A {engine.speed}× cada dia tem {displayDuration(engine.budgetMs)}, e o motor leva{" "}
                {displayDuration(engine.item.mean_ms)}. Na prática, a partida corre a uns {engine.effectiveSpeed}×.
              </AlertDescription>
            </Alert>
          )}

          <KpiCards
            data={data}
            rowsByTotal={rowsByTotal}
            onSeeTable={() => document.getElementById(TABLE_ID)?.scrollIntoView({ behavior: "smooth" })}
          />
          <TimeTable id={TABLE_ID} rows={rows} />
          <div className="grid items-start gap-5 lg:grid-cols-[1.35fr_1fr]">
            <TrafficTable traffic={data.traffic} />
            <PySpyCard pid={data.pid} />
          </div>
        </>
      )}
    </div>
  );
}
