import { Controller, type UseFormReturn } from "react-hook-form";
import { PeriodPicker } from "@/shared/components/period-picker";
import { Field, FieldError, FieldLabel, FieldLegend, FieldSet } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { formatMoney } from "@/shared/lib/utils/format";
import type { CoverageCheck } from "../../lib/coverage";
import type { SimulationFormValues } from "../../lib/simulation-form";
import { CoverageAlerts } from "../coverage-alerts";

type BasicsFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  coverageCheck: CoverageCheck;
  startDate: SimulationFormValues["startDate"];
  gameType: SimulationFormValues["gameType"];
};

/** Nome, período e dinheiro da partida. */
export function BasicsFields({ form, readOnly, coverageCheck, startDate, gameType }: BasicsFieldsProps) {
  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Básico</FieldLegend>
      <Controller
        control={form.control}
        name="name"
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor="rules-name">Nome</FieldLabel>
            <Input {...field} id="rules-name" aria-invalid={fieldState.invalid} />
            <FieldError errors={[fieldState.error]} />
          </Field>
        )}
      />
      <PeriodPicker form={form} readOnly={readOnly} startUncovered={coverageCheck.missingAtStart.length > 0} />
      <CoverageAlerts check={coverageCheck} startDate={startDate} />
      <div className="grid grid-cols-2 gap-3">
        {(
          [
            ["startingCash", "Saldo inicial"],
            ["monthlyContribution", "Aporte mensal"],
          ] as const
        )
          .filter(([name]) => !(gameType === "FINANCIAL_INDEPENDENCE" && name === "monthlyContribution"))
          .map(([name, label]) => (
            <Controller
              key={name}
              control={form.control}
              name={name}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor={`rules-${name}`}>{label}</FieldLabel>
                  <Input
                    {...field}
                    id={`rules-${name}`}
                    inputMode="decimal"
                    numeric
                    aria-invalid={fieldState.invalid}
                    onChange={(e) => field.onChange(formatMoney(e.target.value))}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
          ))}
      </div>
    </FieldSet>
  );
}
