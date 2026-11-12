import { Check } from "lucide-react";
import { PROFESSION_ORDER, PROFESSIONS } from "@/shared/lib/professions";
import { cn } from "@/shared/lib/utils";
import { displayDecimal } from "@/shared/lib/utils/display";
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

/** As 6 profissões em cartões de 3 colunas: o múltiplo da renda sobre o salário do host e o que a profissão sente. */
export function ProfessionCards({ selected, disabled, onSelect }: ProfessionGridProps) {
  return (
    <div className="grid grid-cols-3 gap-3">
      {PROFESSION_ORDER.map((profession) => {
        const { name, icon: Icon, incomeMultiple, feels } = PROFESSIONS[profession];
        const isMine = profession === selected;
        return (
          <button
            key={profession}
            type="button"
            disabled={disabled}
            aria-pressed={isMine}
            onClick={() => onSelect(profession)}
            className={cn(
              "grid min-w-0 cursor-pointer content-start gap-2.5 rounded-xl border bg-card p-4 text-left transition-colors outline-none hover:border-input focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default disabled:opacity-55",
              isMine && "bg-subtle ring-2 ring-foreground",
            )}
          >
            <span className="flex items-center gap-3">
              <span
                className={cn(
                  "grid size-8 shrink-0 place-content-center rounded-lg bg-muted text-muted-foreground",
                  isMine && "bg-foreground text-background",
                )}
              >
                <Icon className="size-4" />
              </span>
              <span className="grid min-w-0">
                <span className="truncate text-sm font-semibold">{name}</span>
                <span className="font-mono text-xs text-muted-foreground">
                  {displayDecimal(incomeMultiple)}× o salário
                </span>
              </span>
            </span>
            <span className="text-[13px] text-muted-foreground">{feels}</span>
          </button>
        );
      })}
    </div>
  );
}
