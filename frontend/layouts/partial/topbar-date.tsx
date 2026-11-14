import { Pause } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";

type TopbarDateProps = {
  /** Data de hoje já formatada; ausente antes do primeiro dado */
  date: string | undefined;
  paused: boolean;
  /** Velocidade máxima destaca a data em azul */
  maxSpeed: boolean;
  /** O motivo da pausa que não foi do jogador */
  pauseHint: string | null;
};

const BASE = "flex h-8 items-center rounded-md px-3 text-[13px]";

/** A data de hoje; na pausa ela vira "Pausado · data" sobre fundo âmbar, com o motivo na dica. */
export function TopbarDate({ date, paused, maxSpeed, pauseHint }: TopbarDateProps) {
  const text = date ?? "—";

  if (!paused) {
    return <span className={cn(BASE, "font-mono", maxSpeed && "bg-info-soft text-info")}>{text}</span>;
  }

  const label = (
    <span
      role="status"
      className={cn(BASE, "gap-1.5 bg-warning-soft font-medium text-warning", pauseHint && "cursor-help")}
    >
      <Pause className="size-3.5" />
      Pausado · <span className="font-mono">{text}</span>
    </span>
  );

  if (!pauseHint) return label;

  return (
    <Tooltip>
      <TooltipTrigger render={label} />
      <TooltipContent>{pauseHint}</TooltipContent>
    </Tooltip>
  );
}
