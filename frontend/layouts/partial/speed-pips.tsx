import { Kbd } from "@/shared/components/ui/kbd";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import { MAX_SPEED, SPEED_OPTIONS } from "./time-shortcuts";

// Cada tracinho é mais alto que o anterior
const PIP_HEIGHTS = ["h-1.5", "h-2.25", "h-3", "h-3.75", "h-4.5"];

type SpeedPipsProps = {
  /** Velocidade da partida; 0 é a pausa */
  speed: number;
  /** Velocidade em que o play retoma, mostrada apagada durante a pausa */
  resumeSpeed: number;
  disabled: boolean;
  onChange: (speed: number) => void;
};

/** Velocidade em tracinhos que sobem, com o número ao lado: um clique por tracinho. */
export function SpeedPips({ speed, resumeSpeed, disabled, onChange }: SpeedPipsProps) {
  const paused = speed === 0;
  const shown = paused ? resumeSpeed : speed;
  const shownIndex = SPEED_OPTIONS.findIndex((option) => option === shown);

  return (
    <div
      role="group"
      aria-label="Velocidade da simulação"
      className="flex h-8 items-center gap-2 rounded-md bg-muted px-2.5"
    >
      <span className="flex items-center">
        {SPEED_OPTIONS.map((option, index) => {
          const on = index <= shownIndex;
          const fast = option === MAX_SPEED;

          return (
            <Tooltip key={option}>
              <TooltipTrigger
                render={
                  <button
                    type="button"
                    aria-label={`Velocidade ${option}×`}
                    aria-pressed={!paused && option === speed}
                    disabled={disabled}
                    onClick={() => onChange(option)}
                    className="flex h-8 w-2.5 cursor-pointer items-end justify-center disabled:cursor-default"
                  />
                }
              >
                <span
                  className={cn(
                    "mb-1.75 w-1.5 rounded-xs",
                    PIP_HEIGHTS[index],
                    fast
                      ? on
                        ? paused
                          ? "bg-info-border"
                          : "bg-info"
                        : "bg-info-border"
                      : on
                        ? paused
                          ? "bg-sidebar-muted"
                          : "bg-foreground"
                        : "bg-input",
                  )}
                />
              </TooltipTrigger>
              <TooltipContent>
                {option}× tecla <Kbd inverse>{index + 1}</Kbd>· <Kbd inverse>Espaço</Kbd> pausa
              </TooltipContent>
            </Tooltip>
          );
        })}
      </span>
      <span
        className={cn(
          "min-w-8.5 text-right font-mono text-xs font-semibold",
          paused ? "text-sidebar-muted" : shown === MAX_SPEED && "text-info",
        )}
      >
        {shown}×
      </span>
    </div>
  );
}
