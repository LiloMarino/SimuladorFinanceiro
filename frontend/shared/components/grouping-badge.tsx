import { Swords, Users } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import type { PlayerGrouping } from "@/types";

/** Selo do modo da sala: o que todos veem, sem trocar de modo (isso é regra do host). */
export function GroupingBadge({ grouping }: { grouping: PlayerGrouping }) {
  return grouping === "TEAMS" ? (
    <Badge variant="info">
      <Users />
      Em equipes
    </Badge>
  ) : (
    <Badge variant="secondary">
      <Swords />
      Todos contra todos
    </Badge>
  );
}
