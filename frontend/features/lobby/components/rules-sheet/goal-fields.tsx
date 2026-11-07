import { Controller, type UseFormReturn } from "react-hook-form";
import { Flag } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel, FieldLegend, FieldSet } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { GOAL_SHORTCUTS } from "@/shared/lib/goal";
import { formatMoney } from "@/shared/lib/utils/format";
import type { SimulationFormValues } from "../../lib/simulation-form";

type GoalFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  /** O saldo inicial em reais, para os atalhos de múltiplo */
  startingCashAmount: number;
  /** A meta em reais, para marcar o atalho que ela coincide */
  goalAmount: number;
};

/** A meta de patrimônio da corrida e o aviso de quem vence. */
export function GoalFields({ form, readOnly, startingCashAmount, goalAmount }: GoalFieldsProps) {
  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Meta</FieldLegend>
      <Controller
        control={form.control}
        name="goalNetWorth"
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor="rules-goalNetWorth">
              Meta de patrimônio
              <InfoHint label="Como funciona a meta">
                <div className="space-y-1 text-left">
                  <p>É o patrimônio (caixa, renda fixa e ações) que um jogador precisa atingir para vencer.</p>
                  <p>Ex.: com saldo inicial de R$ 100.000, a meta de 10× é R$ 1.000.000.</p>
                  <p>
                    Meta alta demais pode não ser alcançada até a data final; nesse caso vence quem chegar mais perto.
                  </p>
                </div>
              </InfoHint>
            </FieldLabel>
            <Input
              {...field}
              id="rules-goalNetWorth"
              inputMode="decimal"
              numeric
              aria-invalid={fieldState.invalid}
              onChange={(e) => field.onChange(formatMoney(e.target.value))}
            />
            <div className="flex flex-wrap gap-1.5">
              {GOAL_SHORTCUTS.map((multiple) => (
                <Button
                  key={multiple}
                  type="button"
                  size="xs"
                  variant={startingCashAmount > 0 && goalAmount === startingCashAmount * multiple ? "info" : "outline"}
                  onClick={() => field.onChange(formatMoney(String(Math.round(startingCashAmount * multiple * 100))))}
                >
                  {multiple}× o saldo inicial
                </Button>
              ))}
            </div>
            <div className="flex items-center gap-1">
              <FieldDescription>Em reais do dia, sem descontar a inflação</FieldDescription>
              <InfoHint label="Meta e inflação">
                Numa partida longa, R$ 1 milhão no fim compra bem menos do que no começo: o valor da meta não acompanha
                os preços.
              </InfoHint>
            </div>
            <FieldError errors={[fieldState.error]} />
          </Field>
        )}
      />
      <Alert variant="info">
        <Flag />
        <AlertTitle>Quem vence já está definido</AlertTitle>
        <AlertDescription>
          A partida termina no dia em que alguém chega à meta. Chegando dois no mesmo dia, vence o maior patrimônio. Se
          ninguém chegar até a data final, vence quem ficou mais perto. Em equipes, conta a média do patrimônio dos
          membros.
        </AlertDescription>
      </Alert>
    </FieldSet>
  );
}
