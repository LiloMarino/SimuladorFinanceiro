import { PlayerAvatar } from "@/shared/components/player-avatar";
import { cn } from "@/shared/lib/utils";
import { partyColor } from "@/shared/lib/party-colors";
import { playerInitials } from "@/shared/lib/player-initials";
import type { PartyCandidate } from "@/types";

const ABBR_SIZES = {
  sm: "h-[18px] px-1 text-[9px]",
  md: "h-5 px-[5px] text-[10px]",
  lg: "h-9 px-[9px] text-[13px]",
} as const;

type PartyMarkProps = {
  abbr: string;
  /** #RRGGBB escolhido pela fundadora; nulo no partido do computador, que tem a cor fixa da sigla */
  color: string | null;
  size?: keyof typeof ABBR_SIZES;
};

/** A sigla do partido na cor dele. */
export function PartyMark({ abbr, color, size = "md" }: PartyMarkProps) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-[5px] font-bold tracking-[.03em] text-white",
        ABBR_SIZES[size],
      )}
      style={{ backgroundColor: partyColor({ abbr, color }) }}
    >
      {abbr}
    </span>
  );
}

type PersonMarkProps = {
  person: PartyCandidate;
  size?: "sm" | "default";
};

/** O avatar de quem concorre: o do jogador, ou um círculo tracejado com as iniciais no candidato do computador. */
export function PersonMark({ person, size = "sm" }: PersonMarkProps) {
  if (person.nickname !== null) {
    return <PlayerAvatar nickname={person.nickname} color={person.color ?? undefined} size={size} />;
  }
  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-full border-[1.5px] border-dashed border-faint-foreground bg-card font-semibold text-muted-foreground",
        size === "sm" ? "size-6 text-[9px]" : "size-8 text-xs",
      )}
    >
      {playerInitials(person.name)}
    </span>
  );
}
