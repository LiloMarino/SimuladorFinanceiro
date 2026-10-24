import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Info, TriangleAlert } from "lucide-react";
import { CoverageBar } from "@/shared/components/coverage-bar";
import { DateField } from "@/shared/components/date-field";
import { InfoHint } from "@/shared/components/info-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import { PRICE_IMPACT_MODE_LABELS } from "@/shared/lib/price-impact";
import type { BacktestCoverage, BacktestPriceImpact } from "@/types";
import { displaySpan } from "../lib/period";
import type { BacktestFormValues } from "../lib/form";
import { ReferenceLegend } from "./reference-legend";

const IMPACT_LEVELS: BacktestPriceImpact[] = ["OFF", "REALISTIC", "STRONG"];

type PeriodCardProps = {
  form: UseFormReturn<BacktestFormValues>;
  coverage: BacktestCoverage;
  /** `side` empilha os campos numa coluna estreita; `wide` os põe numa linha só */
  layout: "side" | "wide";
};

/** Período e dinheiro do backtest: iguais para todas as estratégias. */
export function PeriodCard({ form, coverage, layout }: PeriodCardProps) {
  const [startDate, endDate] = useWatch({ control: form.control, name: ["startDate", "endDate"] });
  const wide = layout === "wide";
  const realEnd = coverage.real_end;
  const bothDates = isIsoDate(startDate) && isIsoDate(endDate);
  const window = bothDates ? { start: startDate, end: endDate } : null;
  const generated = bothDates && !!realEnd && endDate > realEnd;
  // O mercado gerado começa no mês seguinte ao último dado real, ou no início escolhido se ele já for depois
  const futureStart = realEnd ? (startDate > realEnd ? startDate : nextMonth(realEnd)) : null;

  const name = (
    <Controller
      control={form.control}
      name="name"
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid} className="min-w-0">
          <FieldLabel htmlFor="backtest-name">Nome</FieldLabel>
          <Input {...field} id="backtest-name" autoComplete="off" aria-invalid={fieldState.invalid} />
          <FieldError errors={[fieldState.error]} />
        </Field>
      )}
    />
  );

  const dates = (["startDate", "endDate"] as const).map((fieldName) => (
    <Controller
      key={fieldName}
      control={form.control}
      name={fieldName}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid} className="min-w-0">
          <FieldLabel htmlFor={`backtest-${fieldName}`}>{fieldName === "startDate" ? "Início" : "Fim"}</FieldLabel>
          <DateField
            id={`backtest-${fieldName}`}
            value={field.value}
            onChange={(value) => {
              field.onChange(value);
              // Início e fim se validam juntos
              void form.trigger(["startDate", "endDate"]);
            }}
            onBlur={field.onBlur}
            invalid={fieldState.invalid}
            dataEnds={{ realEnd: coverage.real_end ?? undefined, generatedEnd: coverage.generated_end ?? undefined }}
            period={window}
          />
          <FieldError errors={[fieldState.error]} />
        </Field>
      )}
    />
  ));

  const money = (
    [
      ["startingCash", "Saldo inicial"],
      ["monthlyContribution", "Aporte mensal"],
    ] as const
  ).map(([fieldName, label]) => (
    <Controller
      key={fieldName}
      control={form.control}
      name={fieldName}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid} className="min-w-0">
          <FieldLabel htmlFor={`backtest-${fieldName}`}>{label}</FieldLabel>
          <Input
            {...field}
            id={`backtest-${fieldName}`}
            inputMode="decimal"
            numeric
            aria-invalid={fieldState.invalid}
            onChange={(event) => field.onChange(formatMoney(event.target.value))}
          />
          <FieldError errors={[fieldState.error]} />
        </Field>
      )}
    />
  ));

  const impact = (
    <Controller
      control={form.control}
      name="priceImpact"
      render={({ field }) => (
        <Field>
          <div className="flex items-center gap-1.5">
            <FieldLabel>Impacto de preço</FieldLabel>
            <InfoHint label="O que é o impacto de preço">
              Ordem grande move o preço contra quem compra: comprar muito de uma vez paga mais caro, e o efeito some aos
              poucos. Realista e Forte são os mesmos ajustes prontos das regras da partida.
            </InfoHint>
          </div>
          <ToggleGroup
            variant="segmented"
            aria-label="Impacto de preço"
            value={[field.value]}
            onValueChange={(values) => values[0] && field.onChange(values[0])}
            className="w-full"
          >
            {IMPACT_LEVELS.map((level) => (
              <ToggleGroupItem key={level} value={level} className="flex-1">
                {PRICE_IMPACT_MODE_LABELS[level]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          {!wide && <FieldDescription>Ordem grande move o preço contra quem compra.</FieldDescription>}
        </Field>
      )}
    />
  );

  const futureNote = generated && futureStart && (
    <FieldDescription>
      De {displayMonthSlashYear(futureStart)} em diante o mercado é gerado, sorteado de trechos do histórico. Serve
      para ver se a estratégia se sustenta fora do que já aconteceu.
    </FieldDescription>
  );

  const rulesNote = (
    <p className="flex items-start gap-2 rounded-lg bg-subtle px-3 py-2.5 text-[13px] text-muted-foreground">
      <Info className="mt-0.5 size-4 shrink-0" />
      Sem salário, despesas nem imprevistos: todas jogam nas mesmas condições, e rodar de novo dá o mesmo resultado.
    </p>
  );

  return (
    <Card className={cn(!wide && "self-start")}>
      {/* Cabeçalho */}
      <CardHeader>
        <CardTitle>Período e dinheiro</CardTitle>
        {!wide && <CardDescription>Iguais para todas as estratégias.</CardDescription>}
      </CardHeader>

      <CardContent>
        <div className="grid gap-4">
          {wide ? (
            <>
              <div className="grid grid-cols-[1.4fr_140px_140px_170px_170px_auto] items-start gap-3">
                {name}
                {dates}
                {money}
                {impact}
              </div>
              <div className="grid grid-cols-[minmax(0,1fr)_380px] items-center gap-5">
                <CoverageBar coverage={coverage} window={window} />
                <div className="grid gap-2">
                  {futureNote}
                  {rulesNote}
                </div>
              </div>
            </>
          ) : (
            <>
              {name}
              <div className="grid grid-cols-2 gap-2.5">{dates}</div>
              <CoverageBar coverage={coverage} window={window} />
              {futureNote}
              <div className="grid grid-cols-2 gap-2.5">{money}</div>
              {impact}
              {rulesNote}
              <ReferenceLegend />
            </>
          )}

          {generated && futureStart && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>{displaySpan(futureStart <= endDate ? futureStart : endDate, endDate)} de futuro gerado</AlertTitle>
              <AlertDescription>
                De {displayMonthSlashYear(futureStart)} a {displayMonthSlashYear(endDate)} o mercado é sorteado de
                trechos do histórico desde {coverage.first_date?.slice(0, 4)}. O gráfico e o resultado avisam que essa parte
                não aconteceu de verdade.
              </AlertDescription>
            </Alert>
          )}
          {generated && (
            <Alert variant="muted">
              <Info />
              <AlertTitle>Por que testar no gerado?</AlertTitle>
              <AlertDescription>
                Uma estratégia que só ganha no passado real e perde no gerado pode ter tido sorte, e não mérito.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/** O primeiro dia do mês seguinte ao dado: de onde o mercado passa a ser gerado. */
function nextMonth(iso: string) {
  const [year, month] = iso.split("-").map(Number);
  const next = new Date(year, month, 1);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${next.getFullYear()}-${pad(next.getMonth() + 1)}-01`;
}
