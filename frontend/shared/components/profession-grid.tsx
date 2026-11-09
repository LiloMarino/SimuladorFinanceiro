import { Check } from "lucide-react";
import { PROFESSION_ORDER, PROFESSIONS } from "@/shared/lib/professions";
import { cn } from "@/shared/lib/utils";
import type { Profession } from "@/types";

type ProfessionGridProps = {
  /** Profissão do próprio jogador, marcada com o check */
  selected: Profession | null | undefined;
  disabled?: boolean;
  onSelect: (profession: Profession) => void;
};

/** As 6 profissões em grade, cada uma com o que a renda dela sente; profissão não tem dono nem limite de jogadores. */
export function ProfessionGrid({ selected, disabled, onSelect }: ProfessionGridProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {PROFESSION_ORDER.map((profession) => {
        const { name, icon: Icon, feels } = PROFESSIONS[profession];
        const isMine = profession === selected;
        return (
          <button
            key={profession}
            type="button"
            disabled={disabled}
            aria-pressed={isMine}
            onClick={() => onSelect(profession)}
            className={cn(
              "flex min-w-0 cursor-pointer items-start gap-2 rounded-[10px] border border-border bg-card p-2 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default",
              isMine && "bg-subtle ring-2 ring-foreground",
            )}
          >
            <span className="grid size-6 shrink-0 place-content-center">
              {isMine ? <Check className="size-4" /> : <Icon className="size-4 text-muted-foreground" />}
            </span>
            <span className="grid min-w-0 flex-1">
              <span className="truncate text-[13px] font-semibold">{name}</span>
              <span className="text-xs text-muted-foreground">{feels}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
}
