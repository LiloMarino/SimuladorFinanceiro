import type { CSSProperties } from "react";
import { Check, Shield } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TEAMS, teamColor, teamShortName } from "@/shared/lib/teams";
import { cn } from "@/shared/lib/utils";
import type { RoomPlayer, TeamNaming } from "@/types";

type TeamGridProps = {
  /** Quem está em cada equipe: os membros aparecem como avatares pequenos */
  players: RoomPlayer[];
  naming: TeamNaming;
  /** Equipe do próprio jogador, marcada com o check */
  selected: number | null | undefined;
  disabled?: boolean;
  onSelect: (team: number) => void;
};

/** As 10 equipes em grade, cada uma com os membros; a vazia fica à mostra para abrir uma nova. */
export function TeamGrid({ players, naming, selected, disabled, onSelect }: TeamGridProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {TEAMS.map(({ number }) => {
        const members = players.filter((p) => p.team === number);
        const isMine = number === selected;
        return (
          <button
            key={number}
            type="button"
            disabled={disabled}
            aria-pressed={isMine}
            onClick={() => onSelect(number)}
            style={{ "--team": teamColor(number) } as CSSProperties}
            className={cn(
              "flex min-w-0 cursor-pointer items-center gap-2 rounded-[10px] border border-border border-l-[3px] border-l-(--team) bg-card p-2 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default",
              isMine && "bg-[color-mix(in_srgb,var(--team)_8%,transparent)] ring-2 ring-foreground",
            )}
          >
            <span className="grid size-6 shrink-0 place-content-center">
              {isMine ? <Check className="size-4" /> : <Shield className="size-4 fill-(--team) stroke-(--team)" />}
            </span>
            <span className="grid min-w-0 flex-1">
              <span className="truncate text-[13px] font-semibold">{teamShortName(number, naming)}</span>
              {members.length === 0 ? (
                <span className="text-[11px] text-muted-foreground">vazia</span>
              ) : (
                <span className="flex -space-x-1.5">
                  {members.map((member) => (
                    <PlayerAvatar key={member.nickname} nickname={member.nickname} color={member.color} size="sm" />
                  ))}
                </span>
              )}
            </span>
          </button>
        );
      })}
    </div>
  );
}
