import { Check } from "lucide-react";
import { PLAYER_COLORS } from "@/shared/lib/player-colors";
import { playerInitials } from "@/shared/lib/player-initials";
import { cn } from "@/shared/lib/utils";
import type { RoomPlayer } from "@/types";

type PlayerColorGridProps = {
  /** Quem já tem cada cor: a cor fica apagada com a sigla do dono */
  owners: RoomPlayer[];
  /** Cor do próprio jogador, marcada com o check */
  selected: string | undefined;
  disabled?: boolean;
  onSelect: (color: string) => void;
};

/** As 10 cores da paleta em grade; as que já têm dono não podem ser escolhidas. */
export function PlayerColorGrid({ owners, selected, disabled, onSelect }: PlayerColorGridProps) {
  return (
    <div className="grid grid-cols-5 gap-x-1.5 gap-y-2.5">
      {PLAYER_COLORS.map((color) => {
        const owner = owners.find((p) => p.color === color.key);
        const isMine = color.key === selected;
        const taken = owner !== undefined && !isMine;
        return (
          <button
            key={color.key}
            type="button"
            disabled={taken || disabled}
            aria-pressed={isMine}
            aria-label={taken ? `${color.name}, de ${owner.nickname}` : color.name}
            onClick={() => onSelect(color.key)}
            className="grid cursor-pointer justify-items-center gap-1 rounded-lg outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default"
          >
            <span
              className={cn(
                "grid size-10 place-content-center rounded-[10px] text-xs font-semibold",
                taken && "opacity-45",
                isMine && "ring-2 ring-foreground ring-offset-2 ring-offset-popover",
              )}
              style={{ backgroundColor: `var(--${color.key})`, color: color.foreground }}
            >
              {taken && playerInitials(owner.nickname)}
              {isMine && <Check className="size-4.5" />}
            </span>
            <span className={cn("text-[11px]", isMine ? "font-semibold" : "text-muted-foreground")}>{color.name}</span>
          </button>
        );
      })}
    </div>
  );
}
