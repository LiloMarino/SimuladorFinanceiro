import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Gavel, Newspaper, TriangleAlert } from "lucide-react";
import { z } from "zod";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
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
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { STATE_LEVERS, STATE_LEVER_LABEL } from "@/shared/lib/state-lever";
import { displayDayMonth, displayMoneyLarge, displayPercent } from "@/shared/lib/utils/display";
import type { StateCompany, StateCompanySize, StateLever, StateRules } from "@/types";
import { useProposeMeasure } from "../../hooks/mutations/useProposeMeasure";
import { useStateFoundingPreview } from "../../hooks/queries/useStateFoundingPreview";
import { EXPECTED_DIVIDEND, FOUNDING_GDP_PUSH } from "../../lib/government-metrics";
import { SIZE_LABEL, leverEffect, leverOwnedNote } from "../../lib/state-companies";
import { MeasureBudgetEffect } from "../measure-budget-effect";

const foundSchema = z.object({
  name: z.string().trim().min(1, "Dê um nome à empresa.").max(30, "O nome vai até 30 letras."),
  ticker: z.string().regex(/^[A-Z]{4}[0-9]$/, "O ticker tem 4 letras e 1 número, como ENOR3."),
  size: z.enum(["SMALL", "MEDIUM", "LARGE"]),
  lever: z.enum(STATE_LEVERS),
});

type FoundValues = z.infer<typeof foundSchema>;

type FoundStateCompanyDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** As estatais de hoje, para dizer o que o governo já tem em cada alavanca */
  companies: StateCompany[];
  /** As regras da fundação que o painel entrega: fatia do governo e capital de cada porte */
  rules: StateRules;
  /** Dias entre a aprovação e a medida valer */
  vigenceDays: number;
};

type LineProps = { label: React.ReactNode; children: React.ReactNode };

function Line({ label, children }: LineProps) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="flex items-center gap-1.5 text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{children}</dd>
    </div>
  );
}

/** Fundar uma estatal: nome, ticker, alavanca e porte, com o que a fundação faz com a dívida e o PIB; vai ao Congresso como medida. */
export function FoundStateCompanyDialog({
  open,
  onOpenChange,
  companies,
  rules,
  vigenceDays,
}: FoundStateCompanyDialogProps) {
  const propose = useProposeMeasure();

  const form = useForm<FoundValues>({
    resolver: zodResolver(foundSchema),
    defaultValues: { name: "", ticker: "", size: "MEDIUM", lever: "FUEL" },
  });

  const values = useWatch({ control: form.control });
  const parsed = foundSchema.safeParse(values);
  const preview = useStateFoundingPreview(parsed.success ? parsed.data : null);
  const data = preview.data;
  const sizeRule = rules.sizes.find((rule) => rule.size === values.size);
  const capital = Number(sizeRule?.capital ?? 0);
  const governmentPart = Number(sizeRule?.government_debt ?? 0);
  const sharePercent = displayPercent(rules.founding_share, 0);
  const marketPercent = displayPercent(1 - Number(rules.founding_share), 0);

  const submit = form.handleSubmit((fields) =>
    propose.mutate({ kind: "FOUND_STATE_COMPANY", ...fields }, { onSuccess: () => onOpenChange(false) }),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-230">
        <DialogHeader variant="divided">
          <DialogTitle>Fundar uma estatal</DialogTitle>
          <DialogDescription>
            Vai como medida ao Congresso: nome, setor e porte, com o efeito de caixa e de PIB. Aprovada, a empresa abre
            o capital na bolsa.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <form id="found-state-company-form" onSubmit={(event) => void submit(event)} className="grid gap-4">
            {/* Identidade */}
            <div className="grid gap-3 sm:grid-cols-[1fr_9rem]">
              <Controller
                control={form.control}
                name="name"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="state-company-name">Nome</FieldLabel>
                    <Input
                      id="state-company-name"
                      autoComplete="off"
                      maxLength={30}
                      aria-invalid={fieldState.invalid}
                      {...field}
                    />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
              <Controller
                control={form.control}
                name="ticker"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="state-company-ticker">Ticker</FieldLabel>
                    <Input
                      id="state-company-ticker"
                      numeric
                      autoComplete="off"
                      maxLength={5}
                      aria-invalid={fieldState.invalid}
                      {...field}
                      onChange={(event) => field.onChange(event.target.value.toUpperCase().replace(/[^A-Z0-9]/g, ""))}
                    />
                    {fieldState.error ? (
                      <FieldError errors={[fieldState.error]} />
                    ) : (
                      <FieldDescription>4 letras e 1 número.</FieldDescription>
                    )}
                  </Field>
                )}
              />
            </div>

            {/* Alavanca */}
            <Controller
              control={form.control}
              name="lever"
              render={({ field }) => (
                <FieldSet>
                  <FieldLegend variant="label">Setor</FieldLegend>
                  <RadioGroup value={field.value} onValueChange={(value) => field.onChange(value as StateLever)}>
                    {STATE_LEVERS.map((lever) => (
                      <FieldLabel key={lever} htmlFor={`found-lever-${lever}`}>
                        <Field orientation="horizontal">
                          <RadioGroupItem value={lever} id={`found-lever-${lever}`} />
                          <FieldContent>
                            <FieldTitle>{STATE_LEVER_LABEL[lever]}</FieldTitle>
                            <FieldDescription>
                              {leverEffect(rules, lever)}{" "}
                              <b className="font-medium">{leverOwnedNote(companies, lever)}.</b>
                            </FieldDescription>
                          </FieldContent>
                        </Field>
                      </FieldLabel>
                    ))}
                  </RadioGroup>
                </FieldSet>
              )}
            />

            {/* Porte */}
            <Controller
              control={form.control}
              name="size"
              render={({ field }) => (
                <FieldSet>
                  <FieldLegend variant="label">Porte</FieldLegend>
                  <RadioGroup
                    value={field.value}
                    onValueChange={(value) => field.onChange(value as StateCompanySize)}
                    className="sm:grid-cols-3"
                  >
                    {rules.sizes.map((rule) => (
                      <FieldLabel key={rule.size} htmlFor={`found-size-${rule.size}`}>
                        <Field orientation="horizontal">
                          <RadioGroupItem value={rule.size} id={`found-size-${rule.size}`} />
                          <FieldContent>
                            <FieldTitle className="w-full justify-between">
                              {SIZE_LABEL[rule.size]}
                              <span className="font-mono text-xs">{displayMoneyLarge(rule.capital)}</span>
                            </FieldTitle>
                            <FieldDescription>Dívida +{displayMoneyLarge(rule.government_debt)}</FieldDescription>
                          </FieldContent>
                        </Field>
                      </FieldLabel>
                    ))}
                  </RadioGroup>
                </FieldSet>
              )}
            />

            {/* Efeitos da fundação */}
            {data ? (
              <>
                <MeasureBudgetEffect effect={data.measure.budget} />
                <dl className="grid gap-2 rounded-lg border p-3.5 text-[13px]">
                  <Line label={`Fatia do governo (${sharePercent})`}>{displayMoneyLarge(governmentPart)}</Line>
                  <Line label={`Vai à bolsa (${marketPercent})`}>{displayMoneyLarge(capital - governmentPart)}</Line>
                  <Line label="Gasto da fundação">
                    {displayMoneyLarge(data.monthly_spending)} por mês, por {data.spending_months} meses
                  </Line>
                  <Line
                    label={
                      <>
                        {FOUNDING_GDP_PUSH.label}
                        <MetricHint metric={FOUNDING_GDP_PUSH} />
                      </>
                    }
                  >
                    +{FOUNDING_GDP_PUSH.format(data.gdp_push)} ao ano
                  </Line>
                  <Line
                    label={
                      <>
                        {EXPECTED_DIVIDEND.label}
                        <MetricHint metric={EXPECTED_DIVIDEND} />
                      </>
                    }
                  >
                    {EXPECTED_DIVIDEND.format(data.expected_treasury_dividend_year)} por ano
                  </Line>
                </dl>
                <Alert variant="muted">
                  <TriangleAlert />
                  <AlertTitle>Retorno sorteado</AlertTitle>
                  <AlertDescription>
                    A estatal rende em média 8% ao ano, mas o jogo sorteia o desempenho de cada ano: o Tesouro pode
                    receber mais ou menos que o dividendo esperado.
                  </AlertDescription>
                </Alert>
                <Alert variant="info">
                  <Gavel />
                  <AlertTitle>O Congresso vota em {displayDayMonth(data.measure.vote_date)}</AlertTitle>
                  <AlertDescription>
                    Passa com 51 votos Sim de 101, e as bancadas votam como o líder orienta. Aprovada, vale em{" "}
                    {displayDayMonth(data.measure.effective)}, {vigenceDays} dias depois.
                  </AlertDescription>
                </Alert>
              </>
            ) : (
              <p className="text-xs text-muted-foreground">
                Com nome e ticker preenchidos, a dívida, o PIB e o dia da votação aparecem aqui.
              </p>
            )}

            {preview.isError && (
              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>Não deu para calcular a fundação</AlertTitle>
                <AlertDescription>{preview.error.message}</AlertDescription>
              </Alert>
            )}
            {propose.isError && (
              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>Não deu para enviar a medida</AlertTitle>
                <AlertDescription>{propose.error.message}</AlertDescription>
              </Alert>
            )}
          </form>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <span className="mr-auto flex items-center gap-1.5 text-xs text-muted-foreground">
            <Newspaper className="size-3.5" />
            Sai no jornal ao ser aprovada
          </span>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" form="found-state-company-form" disabled={propose.isPending || !data}>
            Enviar ao Congresso
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
