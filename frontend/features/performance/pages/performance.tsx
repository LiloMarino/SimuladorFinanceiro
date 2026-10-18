import { useState } from "react";
import { CircleAlert } from "lucide-react";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useDebugStatus } from "@/shared/hooks/useDebugMode";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/shared/components/ui/alert";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ErrorState } from "@/shared/components/error-state";
import { displayDuration } from "@/shared/lib/utils/display";
import { ControlsBar } from "../components/controls-bar";
import { KpiCards } from "../components/kpi-cards";
import { PySpyCard } from "../components/pyspy-card";
import {
  PerformanceDebugOff,
  PerformanceEmpty,
  PerformanceHostOnly,
  PerformanceLoading,
} from "../components/states";
import { TimeTable } from "../components/time-table";
import { TrafficTable } from "../components/traffic-table";
import { useMetrics, useResetMetrics } from "../hooks/useMetrics";
import { buildRows, engineStatus, sortRows } from "../lib/stats";

const TABLE_ID = "tabela-tempo";

export default function PerformancePage() {
  usePageLabel("Desempenho");
  const { debug, isPending: debugPending } = useDebugStatus();
  const [paused, setPaused] = useState(false);
  const { data, error, isPending, refetch, dataUpdatedAt } = useMetrics({
    paused,
    enabled: debug,
  });
  const reset = useResetMetrics();

  if (debugPending || (debug && isPending)) return <PerformanceLoading />;
  if (!debug) return <PerformanceDebugOff />;
  if (error?.status === 403) return <PerformanceHostOnly />;

  if (!data) {
    return (
      <Card>
        <CardContent>
          <ErrorState
            title="Não deu para ler as medições"
            description="O servidor não respondeu. A coleta continua rodando; só a leitura falhou. Se repetir, o motivo fica em logs/error.log."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      </Card>
    );
  }

  const rows = buildRows(data.items);
  const rowsByTotal = sortRows(rows, "total_ms");
  const engine = engineStatus(data);
  const empty = data.items.length === 0 && data.traffic.length === 0;

  return (
    <div className="grid gap-5">
      <ControlsBar
        paused={paused}
        updatedAt={dataUpdatedAt}
        resetting={reset.isPending}
        onTogglePause={() => setPaused((value) => !value)}
        onReset={() => reset.mutate()}
      />

      {empty ? (
        <PerformanceEmpty />
      ) : (
        <>
          {engine.late && engine.item && engine.budgetMs !== null && (
            <Alert variant="destructive">
              <CircleAlert />
              <AlertTitle>
                O tempo está andando mais devagar que o pedido
              </AlertTitle>
              <AlertDescription>
                A {engine.speed}× cada dia tem{" "}
                {displayDuration(engine.budgetMs)}, e o motor leva{" "}
                {displayDuration(engine.item.mean_ms)}. Na prática, a partida
                corre a uns {engine.effectiveSpeed}×.
              </AlertDescription>
            </Alert>
          )}

          <KpiCards
            data={data}
            rowsByTotal={rowsByTotal}
            onSeeTable={() =>
              document
                .getElementById(TABLE_ID)
                ?.scrollIntoView({ behavior: "smooth" })
            }
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
