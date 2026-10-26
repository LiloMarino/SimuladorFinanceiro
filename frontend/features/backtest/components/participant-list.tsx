import { useWatch, type UseFormReturn } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { paramPills, fromDraft } from "@/shared/lib/strategy-params";
import type { StrategyInfo } from "@/types";
import { MAX_PARTICIPANTS, type BacktestFormValues } from "../lib/form";
import { ParticipantEditor } from "./participant-editor";

type ParticipantListProps = {
  form: UseFormReturn<BacktestFormValues>;
  strategies: StrategyInfo[];
  tickerOptions: string[];
  selected: number;
  onSelect: (index: number) => void;
  onAdd: () => void;
  onDuplicate: (index: number) => void;
  onRemove: (index: number) => void;
};

/** A lista das estratégias à esquerda e, à direita, o editor da escolhida. */
export function ParticipantList({
  form,
  strategies,
  tickerOptions,
  selected,
  onSelect,
  onAdd,
  onDuplicate,
  onRemove,
}: ParticipantListProps) {
  const participants = useWatch({ control: form.control, name: "participants" });
  const full = participants.length >= MAX_PARTICIPANTS;
  const invalid = form.formState.errors.participants;

  return (
    <div className="grid grid-cols-[340px_minmax(0,1fr)]">
      {/* Lista de estratégias */}
      <div className="grid content-start gap-2 pr-5">
        {participants.map((participant, index) => {
          const strategy = strategies.find((s) => s.key === participant.strategyKey) ?? strategies[0];
          if (!strategy) return null;
          const values = fromDraft(strategy.params, participant.drafts[strategy.key] ?? {});
          const summary = values
            ? paramPills(strategy, values)
                .map((pill) => pill.value)
                .join(" · ")
            : "Corrija os parâmetros";
          const hasError = !!(invalid as Record<number, unknown> | undefined)?.[index];
          return (
            <div
              key={index}
              className={cn(
                "flex items-center gap-1 rounded-[10px] border bg-card pr-2",
                index === selected && "border-primary bg-info-soft ring-1 ring-primary",
                hasError && "border-destructive",
              )}
            >
              <button
                type="button"
                aria-label={`Editar ${participant.nickname}`}
                aria-pressed={index === selected}
                onClick={() => onSelect(index)}
                className="flex min-w-0 flex-1 cursor-pointer items-center gap-3 rounded-[10px] px-3 py-2.5 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                <PlayerAvatar nickname={participant.nickname} color={participant.color} bot size="lg" />
                <span className="grid min-w-0 gap-0.5">
                  <span className="truncate font-semibold" title={participant.nickname}>
                    {participant.nickname || "Sem nome"}
                  </span>
                  <span className="truncate text-xs text-muted-foreground" title={`${strategy.name} · ${summary}`}>
                    {strategy.name} · {summary}
                  </span>
                </span>
              </button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={`Remover ${participant.nickname}`}
                onClick={() => onRemove(index)}
              >
                <Trash2 />
              </Button>
            </div>
          );
        })}

        <button
          type="button"
          disabled={full}
          onClick={onAdd}
          className="flex h-14.5 cursor-pointer items-center justify-center gap-2 rounded-[10px] border border-dashed border-info-border bg-info-soft text-[13px] font-semibold text-info outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default disabled:opacity-60"
        >
          <Plus className="size-4" />
          Adicionar estratégia
        </button>
        <p className="mt-1 text-xs text-muted-foreground">
          {full
            ? "Cheio: remova uma para pôr outra. O limite é o das 10 vagas da sala."
            : "Para comparar parâmetros, Duplicar e mude um número: “O Grafista” (50/200) contra “Grafista Ligeiro”."}
        </p>
      </div>

      {/* Editor da escolhida */}
      <div className="min-w-0 border-l pl-5">
        {participants[selected] && (
          <ParticipantEditor
            key={selected}
            form={form}
            index={selected}
            strategies={strategies}
            tickerOptions={tickerOptions}
            canDuplicate={!full}
            onDuplicate={() => onDuplicate(selected)}
            onRemove={() => onRemove(selected)}
          />
        )}
      </div>
    </div>
  );
}
