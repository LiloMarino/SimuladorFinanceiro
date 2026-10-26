import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Copy, Trash2 } from "lucide-react";
import { BotColorSwatches } from "@/shared/components/bot-color-swatches";
import { BotNameField } from "@/shared/components/bot-name-field";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { drawBotName, isDrawnName } from "@/shared/lib/bot-names";
import { GROUP_SECTION } from "@/shared/lib/strategy-groups";
import { defaultValues, draftErrors, toDraft, type ParamDraft } from "@/shared/lib/strategy-params";
import { moneyToBody } from "@/shared/lib/utils/money-field";
import type { StrategyGroup, StrategyInfo } from "@/types";
import type { BacktestFormValues } from "../lib/form";

const GROUPS: StrategyGroup[] = ["reference", "tactic"];

type ParticipantEditorProps = {
  form: UseFormReturn<BacktestFormValues>;
  index: number;
  strategies: StrategyInfo[];
  tickerOptions: string[];
  canDuplicate: boolean;
  onDuplicate: () => void;
  onRemove: () => void;
};

/** Edita uma estratégia participante ao lado da lista: tipo, nome, cor e parâmetros. */
export function ParticipantEditor({
  form,
  index,
  strategies,
  tickerOptions,
  canDuplicate,
  onDuplicate,
  onRemove,
}: ParticipantEditorProps) {
  const participants = useWatch({ control: form.control, name: "participants" });
  const startingCash = useWatch({ control: form.control, name: "startingCash" });
  const participant = participants[index];
  const strategy = strategies.find((s) => s.key === participant?.strategyKey) ?? strategies[0];
  if (!participant || !strategy) return null;

  const draft = participant.drafts[strategy.key] ?? toDraft(defaultValues(strategy));
  const others = participants.filter((_, other) => other !== index);
  const takenNames = others.map((o) => o.nickname);
  const path = `participants.${index}` as const;

  const pickStrategy = (key: string) => {
    const next = strategies.find((s) => s.key === key);
    if (!next || next.key === strategy.key) return;
    form.setValue(`${path}.strategyKey`, next.key);
    // O nome sorteado acompanha a estratégia; o digitado fica
    if (isDrawnName(participant.nickname, strategy)) {
      form.setValue(`${path}.nickname`, drawBotName(next, takenNames), { shouldValidate: true });
    }
  };

  const setDraft = (next: ParamDraft) =>
    form.setValue(`${path}.drafts`, { ...participant.drafts, [strategy.key]: next }, { shouldValidate: true });

  return (
    <div className="grid content-start gap-4">
      {/* Prévia e ações */}
      <div className="flex items-center gap-3">
        <PlayerAvatar nickname={participant.nickname} color={participant.color} bot size="lg" />
        <div className="grid min-w-0 flex-1 gap-0.5">
          <span className="truncate text-base font-semibold">{participant.nickname.trim() || "Sem nome"}</span>
          <span className="text-xs text-muted-foreground">Assim ela aparece no gráfico e no ranking</span>
        </div>
        <Button type="button" variant="outline" size="sm" disabled={!canDuplicate} onClick={onDuplicate}>
          <Copy />
          Duplicar
        </Button>
        <Button type="button" variant="outline-destructive-icon" size="sm" onClick={onRemove}>
          <Trash2 />
          Remover
        </Button>
      </div>

      {/* Estratégia */}
      <Field>
        <FieldLabel>Estratégia</FieldLabel>
        <Select
          value={strategy.key}
          items={Object.fromEntries(strategies.map((s) => [s.key, s.name]))}
          onValueChange={(value) => value && pickStrategy(value)}
        >
          <SelectTrigger size="lg" className="w-full" aria-label="Estratégia">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {GROUPS.map((group) => {
              const items = strategies.filter((s) => s.group === group);
              if (items.length === 0) return null;
              return (
                <SelectGroup key={group}>
                  <SelectLabel>{GROUP_SECTION[group].title}</SelectLabel>
                  {items.map((item) => (
                    <SelectItem key={item.key} value={item.key}>
                      {item.name}
                    </SelectItem>
                  ))}
                </SelectGroup>
              );
            })}
          </SelectContent>
        </Select>
        <FieldDescription>{strategy.summary}</FieldDescription>
      </Field>

      {/* Nome */}
      <Controller
        control={form.control}
        name={`${path}.nickname`}
        render={({ field, fieldState }) => (
          <BotNameField
            id={`participant-${index}-nickname`}
            value={field.value}
            onChange={field.onChange}
            onBlur={field.onBlur}
            error={fieldState.error}
            help="Da lista da estratégia; é o nome no gráfico e no ranking."
            onDraw={() =>
              form.setValue(`${path}.nickname`, drawBotName(strategy, [...takenNames, participant.nickname]), {
                shouldValidate: true,
              })
            }
          />
        )}
      />

      {/* Cor */}
      <Field>
        <FieldLabel>Cor</FieldLabel>
        <BotColorSwatches
          owners={others}
          selected={participant.color}
          onSelect={(next) => form.setValue(`${path}.color`, next, { shouldValidate: true })}
        />
        <FieldDescription>As riscadas já são de outra estratégia.</FieldDescription>
      </Field>

      {/* Parâmetros */}
      <StrategyParamsForm
        key={strategy.key}
        strategy={strategy}
        draft={draft}
        saved={{}}
        compareToDefault
        errors={draftErrors(strategy.params, draft)}
        tickerOptions={tickerOptions}
        cash={moneyToBody(startingCash)}
        cashLabel="o saldo inicial"
        headerAction={
          <Button
            type="button"
            variant="link-muted"
            size="sm"
            onClick={() => setDraft(toDraft(defaultValues(strategy)))}
          >
            Restaurar padrão
          </Button>
        }
        onChange={setDraft}
      />
    </div>
  );
}
