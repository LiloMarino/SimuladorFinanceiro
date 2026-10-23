import { Check } from "lucide-react";
import { PLAYER_COLORS } from "@/shared/lib/player-colors";
import { cn } from "@/shared/lib/utils";
import type { RoomPlayer } from "@/types";

type BotColorSwatchesProps = {
  /** Quem já tem cor na sala: a cor deles aparece riscada */
  owners: RoomPlayer[];
  selected: string;
  onSelect: (color: string) => void;
};

/** As 10 cores da paleta em bolinhas; a escolhida leva o check e as que têm dono ficam riscadas. */
export function BotColorSwatches({ owners, selected, onSelect }: BotColorSwatchesProps) {
  return (
    <div className="flex flex-wrap items-center gap-2.5">
      {PLAYER_COLORS.map((color) => {
        const owner = owners.find((p) => p.color === color.key);
        const isSelected = color.key === selected;
        return (
          <button
            key={color.key}
            type="button"
            disabled={owner !== undefined}
            aria-pressed={isSelected}
            aria-label={owner ? `${color.name}, de ${owner.nickname}` : color.name}
            title={owner ? `${color.name}, de ${owner.nickname}` : color.name}
            onClick={() => onSelect(color.key)}
            className={cn(
              "relative grid size-7 cursor-pointer place-content-center rounded-full outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default",
              owner && "opacity-50",
              isSelected && "ring-2 ring-foreground ring-offset-2 ring-offset-card",
            )}
            style={{ backgroundColor: `var(--${color.key})`, color: color.foreground }}
          >
            {owner && (
              <span
                aria-hidden="true"
                className="absolute inset-0 rounded-full bg-[linear-gradient(135deg,transparent_44%,var(--card)_44%,var(--card)_56%,transparent_56%)]"
              />
            )}
            {isSelected && <Check className="size-3.5" strokeWidth={3} />}
          </button>
        );
      })}
    </div>
  );
}
