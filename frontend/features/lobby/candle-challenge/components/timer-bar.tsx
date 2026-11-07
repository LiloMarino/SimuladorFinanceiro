import { cn } from "@/shared/lib/utils";
import { useCountdown } from "../hooks/useCountdown";
import { isUrgent, secondsLeft, timeFraction } from "../lib/countdown";

interface TimerBarProps {
  remainingMs: number;
  durationMs: number;
}

/** O tempo para responder; nos 2 s finais a barra e o número ficam vermelhos. */
export function TimerBar({ remainingMs, durationMs }: TimerBarProps) {
  const left = useCountdown(remainingMs);
  const urgent = isUrgent(left);

  return (
    <div className="grid gap-1.5" role="timer" aria-label="Tempo para responder">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Responda até fechar</span>
        <b className={cn("font-mono", urgent ? "text-destructive" : "text-primary")}>{secondsLeft(left)} s</b>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            "h-full rounded-full transition-[width] duration-100 ease-linear",
            urgent ? "bg-destructive" : "bg-primary",
          )}
          style={{ width: `${timeFraction(left, durationMs) * 100}%` }}
        />
      </div>
    </div>
  );
}
