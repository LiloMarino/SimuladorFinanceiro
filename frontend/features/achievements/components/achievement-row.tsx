import { Link } from "react-router-dom";
import { AchievementIcon } from "@/shared/components/achievement-icon";
import { Badge } from "@/shared/components/ui/badge";
import { Progress } from "@/shared/components/ui/progress";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { displayShortDate } from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import type { Achievement } from "@/types";
import {
  CATEGORY_LABELS,
  displayProgress,
  displayUnlockedAt,
  displayUnlockedMoment,
  progressFraction,
} from "../lib/format";

export const ROW_GRID = "grid grid-cols-[56px_minmax(0,1fr)_180px_200px] items-center gap-4 px-4.5";

type AchievementRowProps = { achievement: Achievement };

/** Uma conquista da lista: desbloqueada com a data e a partida, bloqueada em cinza com a barra de progresso. */
export function AchievementRow({ achievement }: AchievementRowProps) {
  const { unlock, progress } = achievement;
  // A secreta bloqueada chega sem nome e sem descrição
  const hidden = achievement.name === null;
  const state = unlock ? "unlocked" : hidden ? "secret" : "locked";

  return (
    <li className={cn(ROW_GRID, "border-b border-muted py-3 last:border-b-0", !unlock && "bg-subtle")}>
      <AchievementIcon name={achievement.icon} state={state} />

      {/* Nome, etiquetas e descrição, em uma linha cada; o texto inteiro vem na dica do mouse */}
      <div className="grid min-w-0 gap-0.5">
        <div className="flex min-w-0 items-center gap-1.5">
          <strong
            className={cn("truncate text-sm leading-[1.3] font-semibold", !unlock && "text-secondary-foreground")}
            title={achievement.name ?? undefined}
          >
            {hidden ? "Conquista secreta" : achievement.name}
          </strong>
          {unlock?.is_new && (
            <Badge variant="warning" size="tag">
              Nova
            </Badge>
          )}
          {achievement.secret && (
            <Badge variant="secret" size="tag">
              Secreta
            </Badge>
          )}
        </div>
        <span
          className="truncate text-[13px] leading-[1.4] text-muted-foreground"
          title={achievement.description ?? undefined}
        >
          {hidden ? "O que pede só aparece quando você desbloquear." : achievement.description}
        </span>
      </div>

      <span className="text-[13px] text-muted-foreground">{CATEGORY_LABELS[achievement.category]}</span>

      {/* Desbloqueio ou progresso */}
      {unlock ? (
        <Tooltip>
          <TooltipTrigger render={<Link to={`/match-result/${unlock.simulation_id}`} className="min-w-0 text-right" />}>
            <div className="grid gap-0.5">
              <span className="text-[13px]">{displayUnlockedAt(unlock)}</span>
              <span className="truncate text-xs text-primary">{unlock.simulation_name}</span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="left">
            <div className="grid gap-0.5">
              <span>
                {unlock.simulation_name} · {displayUnlockedMoment(unlock)}
              </span>
              <span className="opacity-70">No jogo: {displayShortDate(unlock.game_date)}</span>
              <span className="opacity-70">Clique para abrir o fechamento da partida</span>
            </div>
          </TooltipContent>
        </Tooltip>
      ) : progress ? (
        <div className="grid gap-1">
          <Progress value={progressFraction(progress) * 100} size="sm" />
          <span className="truncate text-right font-mono text-xs text-muted-foreground tabular-nums">
            {displayProgress(progress)}
          </span>
        </div>
      ) : (
        <span className="text-right text-[13px] text-faint-foreground">Bloqueada</span>
      )}
    </li>
  );
}
