import { useState } from "react";
import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Calculator, ChevronDown, ChevronUp, Lock } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { Switch } from "@/shared/components/ui/switch";
import { ASSISTANCES, summarizeAssistances } from "@/shared/lib/assistance";
import type { SimulationFormValues } from "./lobby-match";

type AssistanceFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  /** Por que as ajudas não mudam, quando não mudam */
  lockNote: string | null;
};

/** "Assistências": o interruptor do Modo Especialista e, por baixo, cada ajuda que ele esconde. */
export function AssistanceFields({ form, readOnly, lockNote }: AssistanceFieldsProps) {
  const [listOpen, setListOpen] = useState(false);
  const shown = useWatch({ control: form.control, name: ASSISTANCES.map((a) => a.field) });
  const { mode } = summarizeAssistances(shown);

  // Ligar o Modo Especialista esconde todas as ajudas; desligar mostra todas
  const setExpertMode = (expert: boolean) => {
    for (const { field } of ASSISTANCES) form.setValue(field, !expert, { shouldValidate: true });
  };

  return (
    <FieldSet disabled={readOnly}>
      <div className="flex items-center gap-2.5">
        <FieldLegend variant="caption" className="mb-0">
          Assistências
        </FieldLegend>
        {lockNote && (
          <span className="ml-auto flex items-center gap-1.5 text-xs text-muted-foreground">
            <Lock className="size-3" />
            {lockNote}
          </span>
        )}
      </div>

      {/* Modo Especialista */}
      <FieldLabel htmlFor="rules-expertMode">
        <Field orientation="horizontal" className="items-center">
          <Switch
            id="rules-expertMode"
            checked={mode === "EXPERT"}
            mixed={mode === "CUSTOM"}
            onCheckedChange={setExpertMode}
            disabled={readOnly}
          />
          <FieldContent>
            <FieldTitle>
              <Calculator className="size-3.5" />
              Modo Especialista
              {mode === "CUSTOM" && <Badge variant="info">Personalizado</Badge>}
            </FieldTitle>
            <FieldDescription>Esconde as ajudas que dão a resposta: você faz as contas.</FieldDescription>
          </FieldContent>
        </Field>
      </FieldLabel>

      <Button
        type="button"
        variant="link"
        size="sm"
        className="w-fit"
        aria-expanded={listOpen}
        onClick={() => setListOpen((open) => !open)}
      >
        {listOpen ? "Ocultar" : "Ajustar uma a uma"}
        {listOpen ? <ChevronUp /> : <ChevronDown />}
      </Button>

      {/* Uma linha por ajuda */}
      {listOpen && (
        <div className="divide-y overflow-hidden rounded-lg border">
          {ASSISTANCES.map(({ field, label, description, scope }) => (
            <Controller
              key={field}
              control={form.control}
              name={field}
              render={({ field: control }) => (
                <div className="px-3 py-2.5">
                  <Field orientation="horizontal" className="items-center">
                    <Switch
                      id={`rules-${field}`}
                      checked={!control.value}
                      onCheckedChange={(hidden) => control.onChange(!hidden)}
                      disabled={readOnly}
                    />
                    <FieldContent>
                      <FieldLabel htmlFor={`rules-${field}`}>
                        <FieldTitle>{label}</FieldTitle>
                      </FieldLabel>
                      <FieldDescription>{description}</FieldDescription>
                    </FieldContent>
                    <Badge variant="secondary">{scope}</Badge>
                  </Field>
                </div>
              )}
            />
          ))}
        </div>
      )}

      <FieldDescription>
        Vale para todos da sala. A pausa e a visão dos outros jogadores seguem como no modo normal.
      </FieldDescription>
    </FieldSet>
  );
}
