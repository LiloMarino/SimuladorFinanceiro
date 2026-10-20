import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Sun, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import {
  displayAnnualExpenseMultiple,
  displayAnnualMultiple,
  displayRatePercent,
  UNEXPECTED_OPTIONS,
  WITHDRAWAL_RATE_RANGE,
} from "@/shared/lib/financial-independence";
import { OVERDRAFT, WITHDRAWAL_RATE } from "@/shared/lib/life-metrics";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoney, displayMoneyCompact, displayMoneyWhole } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import { calculatedGoal, isPositiveMoney, withdrawalRateFraction } from "../lib/life-rules";
import type { SimulationFormValues } from "./lobby-match";

type LifeFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
};

const MONEY_FIELDS = [
  ["monthlySalary", "Salário mensal"],
  ["monthlyExpense", "Despesa mensal"],
] as const;

/** "Vida real" do viver de renda: salário, despesa, imprevistos, IPCA, taxa de retirada e a meta que sai deles. */
export function LifeFields({ form, readOnly }: LifeFieldsProps) {
  const [salary, expense, rate] = useWatch({
    control: form.control,
    name: ["monthlySalary", "monthlyExpense", "withdrawalRate"],
  });
  const expenseAmount = Number(normalizeNumberString(expense));
  const rateFraction = withdrawalRateFraction(rate);
  const goal = calculatedGoal(expense, rate);
  const leftover = Number(normalizeNumberString(salary)) - expenseAmount;
  const budgetValid = isPositiveMoney(salary) && isPositiveMoney(expense);

  // Uma taxa a menos mostra o quanto a meta cresce quando se retira menos
  const lowerRate = rateFraction - 0.01;
  const showLowerRate = goal !== null && lowerRate >= WITHDRAWAL_RATE_RANGE.min - 1e-9;

  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Vida real</FieldLegend>

      {/* Salário e despesa */}
      <div className="grid grid-cols-2 gap-3">
        {MONEY_FIELDS.map(([name, label]) => (
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

      {/* O que sobra por mês */}
      {budgetValid &&
        (leftover >= 0 ? (
          <Alert variant="muted">
            <AlertDescription>
              Sobram <b className="font-mono text-foreground">{displayMoney(leftover)}</b> por mês para investir.
              Salário entra e despesa sai no 1º pregão de cada mês; não há aporte nesta partida.
            </AlertDescription>
          </Alert>
        ) : (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertDescription>
              A despesa passa o salário: faltam <b className="font-mono">{displayMoney(-leftover)}</b> todo mês. A
              partida começa assim mesmo, mas o caixa vai encolher e cair no cheque especial se nada render.
            </AlertDescription>
          </Alert>
        ))}

      {/* Imprevistos */}
      <Controller
        control={form.control}
        name="unexpectedPerYear"
        render={({ field }) => (
          <Field>
            <FieldLabel>Imprevistos</FieldLabel>
            <ToggleGroup
              variant="segmented"
              aria-label="Imprevistos por ano"
              value={[String(field.value)]}
              onValueChange={(values) => values[0] && field.onChange(Number(values[0]))}
              disabled={readOnly}
              className="w-full"
            >
              {UNEXPECTED_OPTIONS.map((option) => (
                <ToggleGroupItem key={option.perYear} value={String(option.perYear)} className="flex-1">
                  {option.label}
                  {option.perYear > 0 && ` · ${option.perYear}/ano`}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            <div className="flex items-start gap-1">
              <FieldDescription>
                Conserto, saúde ou um mês sem salário. Sorteados iguais para todos, nos mesmos dias. Saem do caixa:
                caixa negativo paga juros de cheque especial até ser coberto.
              </FieldDescription>
              <MetricHint metric={OVERDRAFT} />
            </div>
          </Field>
        )}
      />

      {/* Correção pelo IPCA */}
      <Controller
        control={form.control}
        name="inflationAdjusted"
        render={({ field }) => (
          <FieldLabel htmlFor="rules-inflationAdjusted">
            <Field orientation="horizontal">
              <FieldContent>
                <FieldTitle>Corrigir salário e despesa pelo IPCA</FieldTitle>
                <FieldDescription>
                  Uma vez por ano, como um reajuste. A meta sobe junto. Desligado, tudo fica nos reais de hoje.
                </FieldDescription>
              </FieldContent>
              <Switch
                id="rules-inflationAdjusted"
                checked={field.value}
                onCheckedChange={field.onChange}
                disabled={readOnly}
              />
            </Field>
          </FieldLabel>
        )}
      />

      {/* Taxa de retirada e a regra dos 4% */}
      <div className="grid grid-cols-[150px_1fr] items-start gap-3">
        <Controller
          control={form.control}
          name="withdrawalRate"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="rules-withdrawalRate">
                <MetricLabel metric={WITHDRAWAL_RATE} />
              </FieldLabel>
              <InputGroup>
                <InputGroupInput
                  {...field}
                  id="rules-withdrawalRate"
                  inputMode="decimal"
                  numeric
                  aria-invalid={fieldState.invalid}
                  onChange={(e) => field.onChange(e.target.value.replace(/[^\d,]/g, ""))}
                />
                <InputGroupAddon align="inline-end">
                  <InputGroupText>% ao ano</InputGroupText>
                </InputGroupAddon>
              </InputGroup>
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Alert variant="info">
          <AlertDescription>
            {goal === null ? (
              "Informe a despesa e uma taxa entre 1% e 10% para ver a meta."
            ) : (
              <>
                <b>Regra dos 4%:</b> com <b className="font-mono">{displayMoneyCompact(goal)}</b>, retirar{" "}
                {displayRatePercent(rateFraction)} ao ano dá{" "}
                <b className="font-mono">{displayMoneyCompact(expenseAmount * 12)}</b>, os{" "}
                {displayMoneyWhole(expenseAmount)} por mês da sua despesa. O estudo Trinity (dados dos EUA) viu essa
                retirada, corrigida pela inflação, durar 30 anos na maior parte dos períodos.
                {showLowerRate && (
                  <>
                    {" "}
                    Taxa menor deixa a meta maior e mais segura: {displayRatePercent(lowerRate)} pede{" "}
                    {displayAnnualMultiple(lowerRate)} a despesa anual.
                  </>
                )}
              </>
            )}
          </AlertDescription>
        </Alert>
      </div>

      {/* Meta calculada, só leitura */}
      <div className="flex items-center justify-between gap-3 rounded-[10px] bg-sidebar px-3.5 py-3 text-sidebar-foreground">
        <span className="flex min-w-0 items-center gap-2.5">
          <Sun className="size-4 shrink-0 text-sidebar-primary" />
          <span className="grid min-w-0">
            <span className="text-xs">Meta de independência financeira</span>
            <span className="text-xs text-sidebar-muted">
              {goal === null
                ? "Preencha a despesa e a taxa"
                : `${displayAnnualExpenseMultiple(rateFraction)} (${displayMoneyCompact(expenseAmount * 12)}) · vence quem chegar primeiro`}
            </span>
          </span>
        </span>
        <span className="font-mono text-xl font-semibold text-white">{goal === null ? "—" : displayMoney(goal)}</span>
      </div>
    </FieldSet>
  );
}
