import { Link } from "react-router-dom";
import { AchievementIcon } from "@/shared/components/achievement-icon";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useAchievements } from "@/shared/hooks/queries/useAchievements";

type MatchAchievementsProps = { simulationId: number };

/** As conquistas que o jogador desbloqueou nesta partida; sem nenhuma, o bloco não aparece. */
export function MatchAchievements({ simulationId }: MatchAchievementsProps) {
  const { data: achievements } = useAchievements();
  const inThisMatch = (achievements ?? []).filter((a) => a.unlock?.simulation_id === simulationId);
  if (inThisMatch.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Conquistas nesta partida</CardTitle>
        <CardAction>
          <Link to="/achievements" className="text-xs font-medium text-primary hover:underline">
            Ver todas →
          </Link>
        </CardAction>
      </CardHeader>
      <CardContent>
        <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {inThisMatch.map((a) => (
            <li key={a.code} className="flex items-center gap-3">
              <AchievementIcon name={a.icon} state="unlocked" />
              <div className="grid min-w-0">
                <strong className="truncate" title={a.name ?? undefined}>
                  {a.name}
                </strong>
                <span className="truncate text-xs text-muted-foreground" title={a.description ?? undefined}>
                  {a.description}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
