import { useDeferredValue, useState } from "react";
import { Kpi } from "@/shared/components/kpi";
import { MarkedSlider } from "@/shared/components/marked-slider";
import { MetricHint } from "@/shared/components/metric-hint";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displaySpread, displayWholePercent, gradeTone, monthlyEquivalent } from "@/shared/lib/credit";
import { PRICE_TABLE, SELIC_RATE, SPREAD } from "@/shared/lib/credit-metrics";
import { cn, normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayMoney, displayPercent, toCentsString } from "@/shared/lib/utils/display";
import type { CreditOverview } from "@/types";
import { useLoanQuote } from "../hooks/queries/useLoanQuote";
import { InstallmentsDialog } from "./installments-dialog";
import { ReviewLoanDialog } from "./review-loan-dialog";

const MIN_TERM = 6;
const MAX_TERM = 60;
const DEFAULT_TERM = 24;
const DEFAULT_AMOUNT = 50_000;
const TERM_MARKS = [6, 12, 24, 36, 48, 60].map((months) => ({ value: months, label: String(months) }));

type LoanOfferCardProps = {
  overview: CreditOverview;
  /** A oferta só chega aqui com crédito disponível: spread e juro anual definidos (frações do ano) */
  spread: string;
  annualRate: string;
  /** O campo de valor recebe o foco quando a tela pede "Simular um empréstimo" */
  amountInputRef?: React.Ref<HTMLInputElement>;
};

/** "Novo empréstimo": valor, prazo, juro da nota e o que a parcela pede da carteira. */
export function LoanOfferCard({ overview, spread, annualRate: annualRateText, amountInputRef }: LoanOfferCardProps) {
  const { offer } = overview;
  const maxAmount = Number(offer.max_amount);
  const [amountText, setAmountText] = useState(() =>
    formatMoney(toCentsString(String(Math.min(DEFAULT_AMOUNT, Math.floor(maxAmount))))),
  );
  const [termMonths, setTermMonths] = useState(DEFAULT_TERM);
  const [touched, setTouched] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [listing, setListing] = useState(false);

  const amount = Number(normalizeNumberString(amountText)) || 0;
  const excess = Math.max(amount - maxAmount, 0);
  const overLimit = excess > 0;
  const invalid = touched && (amount <= 0 || overLimit);

  // O cálculo acompanha a digitação sem disparar uma consulta por tecla
  const deferredAmount = useDeferredValue(amount);
  const { data: quote } = useLoanQuote(String(deferredAmount), termMonths, { enabled: deferredAmount > 0 });
  const quoteReady = quote !== undefined && deferredAmount === amount && quote.term_months === termMonths;

  const annualRate = Number(annualRateText);
  const spreadRate = Number(offer.selic) + Number(spread);
  const floorApplied = annualRate > spreadRate + 1e-9;
  const debtLimitAmount = Number(offer.debt_limit_amount);
  const currentDebt = Number(overview.debt);
  const thisLoan = Math.min(amount, Math.max(debtLimitAmount - currentDebt, 0));
  const spare = Math.max(debtLimitAmount - currentDebt - thisLoan, 0);
  const portfolioReturn = overview.portfolio_return_12m;

  const setAmount = (value: string) => {
    setTouched(true);
    setAmountText(formatMoney(value));
  };

  return (
    <Card>
      <CardHeader className="grid-cols-[1fr_auto]">
        <div className="grid gap-1">
          <CardTitle>Novo empréstimo</CardTitle>
          <CardDescription>O juro fica travado na assinatura.</CardDescription>
        </div>
        <Badge variant={gradeTone(overview.rating.grade)}>
          Nota {overview.rating.grade} · SELIC {displaySpread(spread)}
        </Badge>
      </CardHeader>

      <CardContent>
        <div className="grid gap-4">
          {/* Valor e prazo */}
          <div className="grid items-start gap-5 sm:grid-cols-2">
            <Field data-invalid={invalid}>
              <FieldLabel htmlFor="loan-amount">Valor</FieldLabel>
              <Input
                id="loan-amount"
                ref={amountInputRef}
                fieldSize="xl"
                numeric
                inputMode="decimal"
                value={amountText}
                aria-invalid={invalid}
                onChange={(event) => setAmount(event.target.value)}
              />
              {overLimit ? (
                <>
                  <FieldError>Passa do seu limite em {displayMoney(excess)}.</FieldError>
                  <Button
                    variant="link"
                    size="sm"
                    className="justify-self-start"
                    onClick={() => setAmount(toCentsString(String(maxAmount)))}
                  >
                    Usar o máximo, {displayMoney(maxAmount)}
                  </Button>
                </>
              ) : amount <= 0 && touched ? (
                <FieldError>Digite quanto quer pegar.</FieldError>
              ) : (
                <FieldDescription>Até {displayMoney(maxAmount)}, o que sobra do seu limite</FieldDescription>
              )}
            </Field>

            <div className="grid gap-2">
              <span className="flex justify-between text-sm font-medium">
                Prazo
                <span className="font-mono">{termMonths} meses</span>
              </span>
              <MarkedSlider
                aria-label="Prazo em meses"
                value={termMonths}
                onValueChange={setTermMonths}
                min={MIN_TERM}
                max={MAX_TERM}
                step={1}
                marks={TERM_MARKS}
              />
            </div>
          </div>

          {/* Juro: SELIC + spread */}
          <div className="flex flex-wrap items-center gap-2 rounded-lg bg-subtle px-3 py-2.5 text-[13px]">
            {floorApplied ? (
              <>
                <span>Renda fixa mais cara do dia</span>
                <b className="font-mono">{displayPercent(offer.best_fixed_income_rate ?? 0)}</b>
                <span className="text-faint-foreground">+</span>
                <span>0,50 p.p.</span>
              </>
            ) : (
              <>
                <span className="inline-flex items-center gap-1">
                  SELIC <MetricHint metric={SELIC_RATE} />
                </span>
                <b className="font-mono">{displayPercent(offer.selic)}</b>
                <span className="text-faint-foreground">+</span>
                <span className="inline-flex items-center gap-1">
                  spread da nota {overview.rating.grade} <MetricHint metric={SPREAD} />
                </span>
                <b className="font-mono">{(Number(spread) * 100).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</b>
              </>
            )}
            <span className="text-faint-foreground">=</span>
            <b className="font-mono">{displayPercent(annualRate)} ao ano</b>
            <span className="text-muted-foreground">({displayPercent(monthlyEquivalent(annualRate))} ao mês)</span>
          </div>

          {/* O custo */}
          <div className="grid gap-4 sm:grid-cols-3">
            <Kpi
              label={
                <>
                  Parcela mensal <MetricHint metric={PRICE_TABLE} />
                </>
              }
              value={quoteReady ? displayMoney(quote.installment) : "—"}
              note={quoteReady ? `${quote.term_months} vezes, todo dia ${quote.due_day}` : "Calculando…"}
            />
            <Kpi
              label="Juro no prazo todo"
              value={quoteReady ? displayMoney(quote.total_interest) : "—"}
              note={quoteReady ? `Você devolve ${displayMoney(quote.total_paid)}` : undefined}
            />
            <Kpi
              label="A carteira precisa render"
              value={`> ${displayPercent(annualRate)} a.a.`}
              note={
                portfolioReturn === null ? (
                  "Menos de 12 meses de histórico"
                ) : (
                  <>
                    Sua carteira rendeu em 12 meses{" "}
                    <b className={cn("font-mono", Number(portfolioReturn) >= annualRate ? "text-success" : "text-destructive")}>
                      {displayPercent(portfolioReturn, 1)}
                    </b>
                  </>
                )
              }
            />
          </div>

          {/* Limite de dívida */}
          <div className="grid gap-1.5">
            <div className="flex justify-between gap-3 text-[13px]">
              <span className="font-medium">Limite de dívida</span>
              <span className="font-mono text-muted-foreground">
                {displayMoney(debtLimitAmount)} · {displayWholePercent(offer.debt_limit)} do patrimônio
              </span>
            </div>
            <StackedBar
              segments={[
                { key: "today", fraction: fractionOf(currentDebt, debtLimitAmount), color: "bg-primary" },
                { key: "loan", fraction: fractionOf(thisLoan, debtLimitAmount), color: "bg-info-border" },
                { key: "spare", fraction: fractionOf(spare, debtLimitAmount), color: "bg-transparent" },
              ]}
            />
            <ul className="flex flex-wrap gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
              <LimitLegend color="bg-primary" label="Dívida de hoje" value={currentDebt} />
              <LimitLegend color="bg-info-border" label="Este empréstimo" value={amount} />
              <LimitLegend color="bg-muted" label="Sobra" value={Math.max(maxAmount - amount, 0)} />
            </ul>
          </div>

          {/* Ações */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" disabled={!quoteReady} onClick={() => setListing(true)}>
              Ver as {termMonths} parcelas
            </Button>
            <Button disabled={!quoteReady || overLimit || amount <= 0} onClick={() => setReviewing(true)}>
              Revisar e assinar
            </Button>
          </div>
        </div>
      </CardContent>

      {quoteReady && (
        <>
          <InstallmentsDialog open={listing} onOpenChange={setListing} quote={quote} />
          <ReviewLoanDialog open={reviewing} onOpenChange={setReviewing} quote={quote} rating={overview.rating} />
        </>
      )}
    </Card>
  );
}

function fractionOf(part: number, whole: number) {
  return whole > 0 ? Math.min(part / whole, 1) : 0;
}

function LimitLegend({ color, label, value }: { color: string; label: string; value: number }) {
  return (
    <li className="flex items-center gap-1.5">
      <span className={cn("size-2.5 rounded-[3px]", color)} aria-hidden="true" />
      {label} <span className="font-mono">{displayMoney(value)}</span>
    </li>
  );
}
