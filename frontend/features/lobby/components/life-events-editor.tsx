import { Controller, useFieldArray, useWatch, type UseFormReturn } from "react-hook-form";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { LifeEventFamily, LifeFrequency } from "@/types";
import { LIFE_EVENT_FAMILIES, LIFE_FREQUENCIES, type SimulationFormValues } from "../lib/simulation-form";

type LifeEventsEditorProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
};

const FAMILY_TEXTS: Record<LifeEventFamily, { title: string; description: string }> = {
  EXPENSES: { title: "Despesas", description: "Conserto, saúde, multa, golpe: dinheiro que sai do caixa." },
  INCOME: { title: "Renda e emprego", description: "Demissão (um mês sem salário) e o revés da profissão." },
  GOOD: { title: "Eventos bons", description: "Restituição, bônus, herança, venda: dinheiro que entra no caixa." },
};

const FREQUENCY_LABELS: Record<LifeFrequency, string> = {
  OFF: "Desligado",
  RARE: "Raro",
  NORMAL: "Normal",
  FREQUENT: "Frequente",
};

/** Os imprevistos da partida por família: a frequência de cada uma e o valor e o liga/desliga de cada tipo. */
export function LifeEventsEditor({ form, readOnly }: LifeEventsEditorProps) {
  const events = useFieldArray({ control: form.control, name: "lifeEvents" });
  const [list, expense] = useWatch({ control: form.control, name: ["lifeEvents", "monthlyExpense"] });
  const expenseAmount = Number(normalizeNumberString(expense));

  return (
    <Field>
      <FieldLabel>Tipos de imprevisto</FieldLabel>
      <FieldDescription>
        Cada família tem a própria frequência: Raro sorteia metade das vezes do normal e Frequente, o dobro. O valor do
        tipo é em despesas mensais: com 2, o imprevisto mexe no caixa o dobro da despesa do mês. Tipo desligado não é
        sorteado.
      </FieldDescription>

      {LIFE_EVENT_FAMILIES.map(([family, frequencyKey]) => (
        <section key={family} className="grid gap-2">
          {/* Cabeçalho da família */}
          <div className="grid gap-1.5">
            <h4 className="text-sm font-medium">{FAMILY_TEXTS[family].title}</h4>
            <p className="text-xs text-muted-foreground">{FAMILY_TEXTS[family].description}</p>
            <Controller
              control={form.control}
              name={`lifeFrequencies.${frequencyKey}`}
              render={({ field }) => (
                <ToggleGroup
                  variant="segmented"
                  aria-label={`Frequência: ${FAMILY_TEXTS[family].title}`}
                  value={[field.value]}
                  onValueChange={(values) => values[0] && field.onChange(values[0])}
                  disabled={readOnly}
                  className="w-full"
                >
                  {LIFE_FREQUENCIES.map((level) => (
                    <ToggleGroupItem key={level} value={level} className="flex-1">
                      {FREQUENCY_LABELS[level]}
                    </ToggleGroupItem>
                  ))}
                </ToggleGroup>
              )}
            />
          </div>

          {/* Tipos da família */}
          <ul className="grid gap-2">
            {events.fields.map((item, index) => {
              const current = list[index];
              if (current?.family !== family) return null;
              const hasValue = current.effect !== "SKIP_NEXT_SALARY";
              const incoming = current.effect === "CASH_IN";
              const multiple = Number(normalizeNumberString(current.expenseMultiple));
              return (
                <li key={item.id} className="grid gap-1.5 rounded-[10px] border border-input px-3 py-2.5">
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
                          aria-label={`Sortear ${current.label}`}
                          className="mt-2"
                        />
                      )}
                    />

                    {/* Nome */}
                    <span className="min-w-0 flex-1 pt-2 text-sm">{current.label}</span>

                    {/* Valor em despesas mensais */}
                    {hasValue ? (
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
                                disabled={readOnly}
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
                  </div>

                  {/* Valor em reais */}
                  {hasValue && Number.isFinite(multiple) && expenseAmount > 0 && (
                    <p className="text-xs text-muted-foreground">
                      Hoje {incoming ? "entram" : "saem"} {displayMoneyWhole(multiple * expenseAmount)}{" "}
                      {incoming ? "no" : "do"} caixa de cada jogador.
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </Field>
  );
}
