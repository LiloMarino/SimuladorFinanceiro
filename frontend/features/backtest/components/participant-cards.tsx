import { Copy, Ellipsis, Pencil, Plus, Trash2 } from "lucide-react";
import { ParamPills } from "@/shared/components/param-pills";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { defaultValues, fromDraft } from "@/shared/lib/strategy-params";
import type { BotFormValues } from "@/shared/lib/bot-form";
import type { StrategyInfo } from "@/types";
import { MAX_PARTICIPANTS } from "../lib/form";

type ParticipantCardsProps = {
  participants: BotFormValues[];
  strategies: StrategyInfo[];
  onAdd: () => void;
  onEdit: (index: number) => void;
  onDuplicate: (index: number) => void;
  onRemove: (index: number) => void;
};

/** As estratégias em cartões: os parâmetros à vista, em azul o que saiu do padrão. */
export function ParticipantCards({
  participants,
  strategies,
  onAdd,
  onEdit,
  onDuplicate,
  onRemove,
}: ParticipantCardsProps) {
  const full = participants.length >= MAX_PARTICIPANTS;

  return (
    <div className="grid grid-cols-3 gap-3">
      {participants.map((participant, index) => {
        const strategy = strategies.find((s) => s.key === participant.strategyKey) ?? strategies[0];
        const values =
          fromDraft(strategy.params, participant.drafts[strategy.key] ?? {}) ?? defaultValues(strategy);
        return (
          <div
            key={index}
            className="grid min-w-0 content-start gap-2.5 rounded-xl border bg-card p-3.5"
          >
            <div className="flex items-center gap-2.5">
              <PlayerAvatar nickname={participant.nickname} color={participant.color} bot size="lg" />
              <div className="grid min-w-0 flex-1">
                <span className="truncate font-semibold" title={participant.nickname}>
                  {participant.nickname}
                </span>
                <span className="truncate text-xs text-muted-foreground">{strategy.name}</span>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger
                  render={
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      className="size-7"
                      aria-label={`Opções de ${participant.nickname}`}
                    />
                  }
                >
                  <Ellipsis className="size-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem variant="destructive" onClick={() => onRemove(index)}>
                    <Trash2 />
                    Remover
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <ParamPills strategy={strategy} values={values} />

            <div className="flex gap-1.5">
              <Button type="button" variant="outline" size="sm" onClick={() => onEdit(index)}>
                <Pencil />
                Editar
              </Button>
              <Button type="button" variant="outline" size="sm" disabled={full} onClick={() => onDuplicate(index)}>
                <Copy />
                Duplicar
              </Button>
            </div>
          </div>
        );
      })}

      <button
        type="button"
        disabled={full}
        onClick={onAdd}
        className="flex min-h-28 cursor-pointer flex-col items-center justify-center gap-1.5 rounded-xl border border-dashed border-info-border bg-info-soft text-[13px] font-semibold text-info outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default disabled:opacity-60"
      >
        <Plus className="size-[18px]" />
        Adicionar estratégia
        <span className="text-xs font-normal text-muted-foreground">
          {full ? "cheio" : `ainda cabem ${MAX_PARTICIPANTS - participants.length}`}
        </span>
      </button>
    </div>
  );
}
