import type { CSSProperties } from "react";
import { Shield } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { teamColor, teamName, teamShortName } from "@/shared/lib/teams";
import type { TeamNaming } from "@/types";

type TeamBadgeProps = {
  /** Índice da equipe; ausente enquanto o jogador não escolheu */
  team: number | null | undefined;
  naming: TeamNaming;
  /** Nome da gestora, quando a equipe leva o nome dela */
  name?: string | null | undefined;
  /** `short` mostra só a cor ("Índigo"); `full`, "Equipe Índigo"; `icon`, só o escudo */
  form?: "short" | "full" | "icon";
  size?: React.ComponentProps<typeof Badge>["size"];
  /** Cor cheia com texto branco, para fundos escuros */
  solid?: boolean;
  className?: string;
};

/** Selo da equipe: escudo na cor dela (a bolinha é do jogador). Sem equipe vira "Sem equipe". */
export function TeamBadge({ team, naming, name, form = "short", size, solid, className }: TeamBadgeProps) {
  if (!team) {
    return (
      <Badge variant="secondary" size={size} className={className}>
        Sem equipe
      </Badge>
    );
  }

  const label = form === "full" ? teamName(team, naming, name) : teamShortName(team, naming, name);
  return (
    <Badge
      variant={solid ? "team-solid" : "team"}
      size={size}
      className={className}
      style={{ "--team": teamColor(team) } as CSSProperties}
      aria-label={teamName(team, naming, name)}
    >
      <Shield />
      {form !== "icon" && label}
    </Badge>
  );
}
