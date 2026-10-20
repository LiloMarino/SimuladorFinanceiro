import { Trophy } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { cn } from "@/shared/lib/utils";
import type { OverviewReport } from "@/types";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import { displayCriterionValue, rankingMeasure } from "../../lib/criterion";

// Degraus na ordem visual: 2º à esquerda, 1º no meio e mais alto, 3º à direita
const STEPS = [
  { position: 2, height: "h-[110px]" },
  { position: 1, height: "h-[150px]" },
  { position: 3, height: "h-20" },
] as const;

interface PodiumProps {
  report: OverviewReport;
  currentPlayerName?: string;
}

/** Os três primeiros pelo critério de vitória, sobre o fundo escuro do topo. */
export function Podium({ report, currentPlayerName }: PodiumProps) {
  const byPosition = new Map(report.players.map((p) => [p.position, p]));
  const measure = rankingMeasure(report);

  return (
    <div className="flex w-full max-w-[480px] items-end gap-3">
      {STEPS.map((step) => {
        const player = byPosition.get(step.position);
        const first = step.position === 1;
        return (
          <div key={step.position} className="flex flex-1 flex-col items-center gap-2">
            {player ? (
              <>
                {first && <Trophy className="size-[26px] text-trophy" />}
                <PlayerAvatar nickname={player.player_nickname} color={player.color} size={first ? "2xl" : "xl"} />
                <span className={cn("max-w-full truncate font-semibold text-white", first ? "text-lg" : "text-[15px]")}>
                  {player.player_nickname}
                  {player.player_nickname === currentPlayerName && " (você)"}
                </span>
                <span className={cn("font-mono text-[13px]", first ? "text-trophy" : "text-sidebar-muted")}>
                  {displayCriterionValue(measure, player.criterion_value)}
                  {measure === "GOAL" && ` · ${displayMoneyCompact(player.total_networth)}`}
                </span>
              </>
            ) : (
              <span className="text-sidebar-muted">Sem {step.position}º lugar</span>
            )}
            <div
              className={cn(
                "flex w-full justify-center rounded-t-[10px] pt-2.5",
                step.height,
                first ? "bg-linear-to-b from-primary to-primary-hover" : "bg-sidebar-accent",
              )}
            >
              <span className="font-mono text-[22px] font-semibold text-white">{step.position}º</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
