import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress, ProgressGenerated } from "@/shared/components/ui/progress";
import { displayMonthSlashYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { BacktestProgress } from "@/types";
import { displaySecondsLeft } from "../lib/period";

type RunningProgressProps = {
  progress: BacktestProgress;
  /** Até onde o mercado é real; o resto do caminho é gerado */
  realEnd: string | null;
};

/** O mês simulado agora, a barra do caminho todo (com o trecho gerado listrado) e quanto falta. */
export function RunningProgress({ progress, realEnd }: RunningProgressProps) {
  const { start_date: start, end_date: end, total_days: total, done_days: done } = progress;
  const percent = total > 0 ? (done / total) * 100 : 0;
  const startTime = parseLocalDate(start).getTime();
  const span = parseLocalDate(end).getTime() - startTime;
  const generatedFrom = realEnd && realEnd < end ? Math.max((parseLocalDate(realEnd).getTime() - startTime) / span, 0) : null;

  return (
    <Card>
      <CardContent>
        <div className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-6">
          {/* Mês simulado */}
          <div className="grid gap-0.5">
            <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">Simulando</span>
            <span className="font-mono text-[28px] leading-tight font-semibold">
              {displayMonthSlashYear(progress.current_date ?? start)}
            </span>
          </div>

          {/* Barra do caminho todo */}
          <div className="grid gap-2">
            <Progress
              value={percent}
              size="lg"
              aria-label="Andamento do backtest"
              markers={generatedFrom === null ? undefined : <ProgressGenerated from={generatedFrom} to={1} />}
            />
            <div className="flex justify-between font-mono text-xs text-faint-foreground">
              <span>{displayMonthSlashYear(start)}</span>
              {generatedFrom !== null && <span>futuro gerado</span>}
              <span>{displayMonthSlashYear(end)}</span>
            </div>
          </div>

          {/* Percentual e tempo que falta */}
          <div className="grid gap-0.5 text-right">
            <span className="font-mono text-xl font-semibold">{Math.floor(percent)}%</span>
            <span className="text-xs text-muted-foreground">
              {done.toLocaleString("pt-BR")} de {total.toLocaleString("pt-BR")} pregões
              {progress.seconds_left !== null && ` · faltam ${displaySecondsLeft(progress.seconds_left)}`}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
