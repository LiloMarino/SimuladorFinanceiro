import { FlaskConical } from "lucide-react";
import { Progress } from "@/shared/components/ui/progress";
import { useBacktestStatus } from "@/shared/hooks/queries/useBacktestStatus";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";

/** Avisa a sala de que o host roda um backtest: ninguém inicia partida até ele terminar. */
export function BacktestBanner() {
  const { data: backtest } = useBacktestStatus();
  const progress = backtest?.progress;
  if (!progress) return null;

  const percent = progress.total_days > 0 ? Math.floor((progress.done_days / progress.total_days) * 100) : 0;

  return (
    <div className="grid gap-2.5 rounded-xl bg-sidebar px-4 py-3 text-[13px] text-sidebar-foreground">
      <span className="flex items-center gap-2">
        <FlaskConical className="size-4 text-sidebar-primary" />
        <span>
          <b className="text-white">{progress.host_nickname} está rodando um backtest</b>
          {progress.current_date && ` · ${displayMonthSlashYear(progress.current_date)}`}
        </span>
        <span className="ml-auto font-mono text-white">{percent}%</span>
      </span>
      <Progress value={percent} size="sm" tone="inverse" aria-label="Andamento do backtest" />
      <span className="text-xs opacity-70">
        A sala volta quando o backtest terminar. Dá para entrar e sair; o resultado aparece em Simulações salvas.
      </span>
    </div>
  );
}
