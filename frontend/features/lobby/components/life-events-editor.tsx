import { Controller, useFieldArray, useWatch, type UseFormReturn } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import {
  FACTORY_LIFE_EVENT_KEYS,
  LIFE_EVENT_EFFECTS,
  newLifeEvent,
  type SimulationFormValues,
} from "../lib/simulation-form";

type LifeEventsEditorProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
};

/** Os tipos de imprevisto da partida: valor de cada um, liga/desliga e os tipos próprios do host. */
export function LifeEventsEditor({ form, readOnly }: LifeEventsEditorProps) {
  const events = useFieldArray({ control: form.control, name: "lifeEvents" });
  const [list, expense] = useWatch({ control: form.control, name: ["lifeEvents", "monthlyExpense"] });
  const expenseAmount = Number(normalizeNumberString(expense));

  return (
    <Field>
      <FieldLabel>Tipos de imprevisto</FieldLabel>
      <FieldDescription>
        O valor é em despesas mensais: com 2, o imprevisto tira do caixa o dobro da despesa do mês. Tipo desligado não é
        sorteado.
      </FieldDescription>

      {/* Lista de tipos */}
      <ul className="grid gap-2">
        {events.fields.map((item, index) => {
          const current = list[index];
          const factory = FACTORY_LIFE_EVENT_KEYS.has(item.key);
          const cashOut = current?.effect === "CASH_OUT";
          const multiple = Number(normalizeNumberString(current?.expenseMultiple));
          return (
            <li key={item.id} className="grid gap-2 rounded-[10px] border border-input px-3 py-2.5">
              <div className="flex items-start gap-3">
                {/* Liga e desliga */}
                <Controller
                  control={form.control}
                  name={`lifeEvents.${index}.enabled`}
                  render={({ field }) => (
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={readOnly}
                      aria-label={`Sortear ${current?.label ?? "imprevisto"}`}
                      className="mt-2"
                    />
                  )}
                />

                {/* Nome */}
                <Controller
                  control={form.control}
                  name={`lifeEvents.${index}.label`}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid} className="min-w-0 flex-1">
                      {factory ? (
                        <span className="pt-2 text-sm">{field.value}</span>
                      ) : (
                        <Input {...field} aria-label="Nome do imprevisto" aria-invalid={fieldState.invalid} />
                      )}
                      <FieldError errors={[fieldState.error]} />
                    </Field>
                  )}
                />

                {/* Valor em despesas mensais */}
                {cashOut ? (
                  <Controller
                    control={form.control}
                    name={`lifeEvents.${index}.expenseMultiple`}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid} className="w-36 shrink-0">
                        <InputGroup>
                          <InputGroupInput
                            {...field}
                            inputMode="decimal"
                            numeric
                            aria-label={`Valor de ${current.label} em despesas mensais`}
                            aria-invalid={fieldState.invalid}
                            onChange={(e) => field.onChange(e.target.value.replace(/[^\d,]/g, ""))}
                          />
                          <InputGroupAddon align="inline-end">
                            <InputGroupText>× despesa</InputGroupText>
                          </InputGroupAddon>
                        </InputGroup>
                        <FieldError errors={[fieldState.error]} />
                      </Field>
                    )}
                  />
                ) : (
                  <span className="w-36 shrink-0 pt-2 text-right text-xs text-muted-foreground">
                    Sem salário no mês seguinte
                  </span>
                )}

                {/* Remover tipo próprio */}
                {!factory && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    aria-label={`Remover ${current?.label ?? "imprevisto"}`}
                    onClick={() => events.remove(index)}
                  >
                    <Trash2 />
                  </Button>
                )}
              </div>

              {/* Efeito do tipo próprio e o valor em reais */}
              {!factory && (
                <Controller
                  control={form.control}
                  name={`lifeEvents.${index}.effect`}
                  render={({ field }) => (
                    <ToggleGroup
                      variant="segmented"
                      aria-label="Efeito do imprevisto"
                      value={[field.value]}
                      onValueChange={(values) => values[0] && field.onChange(values[0])}
                      disabled={readOnly}
                      className="w-full"
                    >
                      {LIFE_EVENT_EFFECTS.map(([effect, label]) => (
                        <ToggleGroupItem key={effect} value={effect} className="flex-1">
                          {label}
                        </ToggleGroupItem>
                      ))}
                    </ToggleGroup>
                  )}
                />
              )}
              {cashOut && Number.isFinite(multiple) && expenseAmount > 0 && (
                <p className="text-xs text-muted-foreground">
                  Hoje sai {displayMoneyWhole(multiple * expenseAmount)} do caixa de cada jogador.
                </p>
              )}
            </li>
          );
        })}
      </ul>

      {/* Adicionar tipo */}
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={readOnly}
        onClick={() => events.append(newLifeEvent())}
      >
        <Plus />
        Adicionar tipo
      </Button>
    </Field>
  );
}
