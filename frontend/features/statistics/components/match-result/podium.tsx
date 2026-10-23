import { Trophy } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { cn } from "@/shared/lib/utils";
import type { OverviewReport } from "@/types";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import { displayCriterionValue, rankingMeasure } from "../../lib/criterion";
import { PodiumSteps } from "./podium-steps";

interface PodiumProps {
  report: OverviewReport;
  currentPlayerName?: string;
}

/** Os três primeiros pelo critério de vitória, sobre o fundo escuro do topo. */
export function Podium({ report, currentPlayerName }: PodiumProps) {
  const measure = rankingMeasure(report);

  return (
    <PodiumSteps
      items={report.players}
      emptyLabel={(position) => `Sem ${position}º lugar`}
      stepClassName={(_, first) => (first ? "bg-linear-to-b from-primary to-primary-hover" : "bg-sidebar-accent")}
      renderEntry={(player, first) => (
        <>
          {first && <Trophy className="size-[26px] text-trophy" />}
          <PlayerAvatar nickname={player.player_nickname} color={player.color} bot={player.is_bot} size={first ? "2xl" : "xl"} />
          <span className={cn("max-w-full truncate font-semibold text-white", first ? "text-lg" : "text-[15px]")}>
            {player.player_nickname}
            {player.player_nickname === currentPlayerName && " (você)"}
          </span>
          <span className={cn("font-mono text-[13px]", first ? "text-trophy" : "text-sidebar-muted")}>
            {displayCriterionValue(measure, player.criterion_value)}
            {measure === "GOAL" && ` · ${displayMoneyCompact(player.total_networth)}`}
          </span>
        </>
      )}
    />
  );
}
