import { Medal, Trophy } from "lucide-react";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayMoney, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, VictoryCriterion } from "@/types";

type Player = OverviewReport["players"][number];

// Degraus na ordem visual: 2º à esquerda, 1º no meio e mais alto, 3º à direita
const STEPS = [
  { position: 2, height: "h-24", medal: "text-slate-400" },
  { position: 1, height: "h-32", medal: "text-yellow-500" },
  { position: 3, height: "h-16", medal: "text-amber-700" },
] as const;

function criterionValue(player: Player, criterion: VictoryCriterion) {
  switch (criterion) {
    case "SCORE":
      return player.score ? `${displayNumber(player.score.total, 0)} pts` : "sem nota";
    case "RETURN":
      return displayPercent(player.return_percent);
    case "NETWORTH":
      return displayMoney(player.total_networth);
    case "SHARPE":
      return player.sharpe_ratio === null ? "—" : displayNumber(player.sharpe_ratio);
  }
}

interface PodiumProps {
  report: OverviewReport;
}

/** Os três primeiros pelo critério de vitória da partida. */
export function Podium({ report }: PodiumProps) {
  const byPosition = new Map(report.players.map((p) => [p.position, p]));

  return (
    <Card>
      <CardContent className="space-y-4 pt-2">
        <p className="text-center text-sm text-muted-foreground">
          Vitória por: <span className="font-semibold text-foreground">{VICTORY_CRITERIA[report.criterion].label}</span>
        </p>

        <div className="mx-auto flex max-w-xl items-end justify-center gap-3">
          {STEPS.map((step) => {
            const player = byPosition.get(step.position);
            return (
              <div key={step.position} className="flex flex-1 flex-col items-center gap-2">
                {player ? (
                  <>
                    {step.position === 1 ? (
                      <Trophy className={`size-8 ${step.medal}`} />
                    ) : (
                      <Medal className={`size-6 ${step.medal}`} />
                    )}
                    <p className="max-w-full truncate text-center font-semibold">{player.player_nickname}</p>
                    <p className="text-sm text-muted-foreground">{criterionValue(player, report.criterion)}</p>
                  </>
                ) : (
                  <p className="text-sm text-muted-foreground">—</p>
                )}
                <div
                  className={`flex w-full items-start justify-center rounded-t-md bg-primary/15 pt-2 text-2xl font-bold ${step.height}`}
                >
                  {step.position}º
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
