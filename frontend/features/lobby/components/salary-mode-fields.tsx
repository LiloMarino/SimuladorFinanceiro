import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Equal, Shapes, type LucideIcon } from "lucide-react";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { PROFESSION_ORDER, PROFESSIONS, professionIncome } from "@/shared/lib/professions";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoney } from "@/shared/lib/utils/display";
import type { SalaryMode } from "@/types";
import type { SimulationFormValues } from "../lib/simulation-form";

const SALARY_MODE_OPTIONS: { value: SalaryMode; label: string; description: string; icon: LucideIcon }[] = [
  {
    value: "EQUAL",
    label: "Salário igual",
    description: "Todos ganham o salário acima, como CLT.",
    icon: Equal,
  },
  {
    value: "PROFESSIONS",
    label: "Uma profissão por jogador",
    description: "Cada um escolhe a sua: muda o que entra por mês e o que o governo e a economia fazem com a renda.",
    icon: Shapes,
  },
];

type SalaryModeFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
};

/** Como o salário da partida vira renda: igual para todos ou por profissão, com a renda de cada uma sobre o salário digitado. */
export function SalaryModeFields({ form, readOnly }: SalaryModeFieldsProps) {
  const [mode, salary] = useWatch({ control: form.control, name: ["salaryMode", "monthlySalary"] });
  const salaryAmount = Number(normalizeNumberString(salary));

  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Renda dos jogadores</FieldLegend>
      <Controller
        control={form.control}
        name="salaryMode"
        render={({ field }) => (
          <RadioGroup
            value={field.value}
            onValueChange={(value) => field.onChange(value as SalaryMode)}
            disabled={readOnly}
            className="grid-cols-2"
          >
            {SALARY_MODE_OPTIONS.map((option) => (
              <FieldLabel key={option.value} htmlFor={`salary-mode-${option.value}`}>
                <Field orientation="horizontal">
                  <RadioGroupItem value={option.value} id={`salary-mode-${option.value}`} />
                  <FieldContent>
                    <FieldTitle>
                      <option.icon className="size-3.5 text-muted-foreground" />
                      {option.label}
                    </FieldTitle>
                    <FieldDescription>{option.description}</FieldDescription>
                  </FieldContent>
                </Field>
              </FieldLabel>
            ))}
          </RadioGroup>
        )}
      />

      {/* Renda de cada profissão sobre o salário digitado */}
      {mode === "PROFESSIONS" && (
        <div className="grid gap-1 rounded-[10px] border p-3">
          <span className="text-xs text-muted-foreground">
            Renda no 1º mês, sobre o salário acima. A despesa e a meta continuam as mesmas para todos.
          </span>
          {PROFESSION_ORDER.map((profession) => {
            const { name, icon: Icon } = PROFESSIONS[profession];
            return (
              <div key={profession} className="flex items-baseline justify-between gap-3 border-t border-muted py-1.5">
                <span className="flex items-center gap-1.5 text-[13px] font-semibold">
                  <Icon className="size-3.5 text-muted-foreground" />
                  {name}
                </span>
                <span className="font-mono font-semibold whitespace-nowrap">
                  {salaryAmount > 0 ? displayMoney(professionIncome(profession, salaryAmount)) : "—"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </FieldSet>
  );
}
