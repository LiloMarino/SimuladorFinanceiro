import { Info, Square } from "lucide-react";
import { Navigate, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { BacktestBadge } from "@/shared/components/backtest-badge";
import { PlayerLineChart } from "@/shared/components/player-line-chart";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { displayMoney, displayMoneyCompact, displayMonthSlashYear } from "@/shared/lib/utils/display";
import { DiscardDialog } from "../components/discard-dialog";
import { RunningProgress } from "../components/running-progress";
import { RunningRanking } from "../components/running-ranking";
import { useDiscardBacktest } from "../hooks/mutations/useDiscardBacktest";
import { useStopBacktest } from "../hooks/mutations/useStopBacktest";
import { useBacktestSetup } from "../hooks/queries/useBacktestSetup";
import { useBacktestStatus } from "@/shared/hooks/queries/useBacktestStatus";
import type { BacktestProgress, BacktestStatus } from "@/types";
import { chartSeries } from "@/shared/lib/backtest-chart-series";

/** O backtest rodando: o mês simulado, o gráfico que anda a cada 20 pregões e a classificação de agora. */
export default function BacktestRunningPage() {
  const navigate = useNavigate();
  const { data: status, isPending } = useBacktestStatus();
  const stop = useStopBacktest();
  const discard = useDiscardBacktest();

  // O fim chega para todos: concluído e parado abrem o relatório; descartado volta ao lobby
  useRealtime("backtest_ended", (event) => {
    void navigate(event.reason === "discarded" ? "/lobby" : `/match-result/${event.simulation_id}`, { replace: true });
  });
  useRealtime("backtest_progress", (event) => {
    event.failures.forEach((failure) =>
      toast.error(`${failure.nickname} parou de operar`, {
        description: "O backtest segue com as outras. Os detalhes técnicos ficam no relatório, na aba Operações.",
      }),
    );
  });

  if (isPending || !status) return <RunningSkeleton />;
  // Sem backtest em andamento não há o que mostrar aqui
  if (!status.progress) return <Navigate to="/lobby" replace />;

  const { progress, participants, points, failures } = status;

  return (
    <div className="grid gap-5">
      {/* Cabeçalho */}
      <div className="flex items-end justify-between gap-4">
        <div className="grid gap-1">
          <h1 className="flex items-center gap-2.5 text-2xl font-bold">
            {progress.name}
            <BacktestBadge />
          </h1>
          <p className="text-sm text-muted-foreground">
            Rodando · {displayMonthSlashYear(progress.start_date)} → {displayMonthSlashYear(progress.end_date)} ·{" "}
            {participants.length} {participants.length === 1 ? "estratégia" : "estratégias"}
          </p>
        </div>
        <div className="flex gap-2">
          <DiscardDialog
            progress={progress}
            pending={discard.isPending}
            onDiscard={() => discard.mutate(undefined, { onSuccess: () => void navigate("/lobby", { replace: true }) })}
          />
          <Button
            type="button"
            variant="dark"
            disabled={stop.isPending}
            onClick={() =>
              stop.mutate(undefined, {
                onSuccess: (stopped) => void navigate(`/match-result/${stopped.simulation_id}`, { replace: true }),
              })
            }
          >
            {stop.isPending ? <Spinner /> : <Square />}
            Parar e ver o resultado
          </Button>
        </div>
      </div>

      <Running progress={progress} participants={participants} points={points} failures={failures} />

      {/* A sala espera */}
      <div className="flex items-center gap-3 rounded-xl bg-sidebar px-4 py-3 text-[13px] text-sidebar-foreground">
        <Info className="size-4 shrink-0 text-sidebar-primary" />
        <span>
          <b className="text-white">A sala está esperando.</b> Quem está na sala vê este andamento no lobby; ninguém inicia
          partida até o backtest terminar.
        </span>
      </div>
    </div>
  );
}

type RunningProps = Pick<BacktestStatus, "participants" | "points" | "failures"> & {
  progress: BacktestProgress;
};

/** Barra, gráfico e classificação: dependem da lista de estratégias e da cobertura do mercado. */
function Running({ progress, participants, points, failures }: RunningProps) {
  const { data: strategies } = useBotStrategies(progress.start_date);
  const { data: setup } = useBacktestSetup();

  return (
    <>
      <RunningProgress progress={progress} realEnd={setup?.coverage.real_end ?? null} />

      <div className="grid grid-cols-[minmax(0,1fr)_360px] items-start gap-5">
        {/* Gráfico */}
        <Card>
          <CardHeader>
            <CardTitle>Patrimônio de cada estratégia</CardTitle>
            <CardDescription>
              O gráfico anda a cada 20 pregões, e o eixo cresce junto. A linha cinza é quanto foi aportado: acima dela, a
              estratégia ganhou dinheiro.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PlayerLineChart
              series={chartSeries(participants, points)}
              format={displayMoney}
              axisFormat={displayMoneyCompact}
              emptyMessage="O primeiro ponto chega em instantes"
            />
          </CardContent>
        </Card>

        {/* Classificação de agora */}
        <RunningRanking participants={participants} strategies={strategies ?? []} point={points.at(-1)} failures={failures} />
      </div>
    </>
  );
}

function RunningSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando o backtest">
      <Skeleton className="h-9 w-1/3" />
      <Skeleton className="h-20" />
      <div className="grid grid-cols-[minmax(0,1fr)_360px] gap-5">
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
    </div>
  );
}
