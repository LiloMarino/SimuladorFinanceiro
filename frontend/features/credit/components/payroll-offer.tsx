import { Info, RefreshCw, TriangleAlert } from "lucide-react";
import { useDeferredValue, useState } from "react";
import { Kpi } from "@/shared/components/kpi";
import { MarkedSlider } from "@/shared/components/marked-slider";
import { MetricHint } from "@/shared/components/metric-hint";
import { StackedBar } from "@/shared/components/stacked-bar";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { PAYROLL_MARGIN } from "@/shared/lib/credit-metrics";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import {
  displayDate,
  displayMonthName,
  displayMoney,
  displayPercent,
  parseLocalDate,
  toCentsString,
} from "@/shared/lib/utils/display";
import type { CreditOverview, PayrollQuote } from "@/types";
import { usePayrollQuote } from "../hooks/queries/usePayrollQuote";
import { InstallmentsDialog } from "./installments-dialog";
import { ReviewPayrollDialog } from "./review-payroll-dialog";

const MIN_TERM = 6;
const MAX_TERM = 60;
const DEFAULT_TERM = 12;
const DEFAULT_AMOUNT = 5_000;
const TERM_MARKS = [6, 12, 24, 36, 48, 60].map((months) => ({ value: months, label: String(months) }));

type PayrollOfferProps = {
  overview: CreditOverview;
  /** O dia da partida: a simulação vale para ele */
  currentDate: string;
};

/** A aba "Consignado" do novo empréstimo: valor e prazo contra a margem do salário e o limite de dívida. */
export function PayrollOffer({ overview, currentDate }: PayrollOfferProps) {
  const [amountText, setAmountText] = useState(() => formatMoney(toCentsString(String(DEFAULT_AMOUNT))));
  const [termMonths, setTermMonths] = useState(DEFAULT_TERM);
  const [reviewing, setReviewing] = useState(false);
  const [listing, setListing] = useState(false);

  const amount = Number(normalizeNumberString(amountText)) || 0;
  const deferredAmount = useDeferredValue(amount);
  const {
    data: quote,
    error,
    refetch,
  } = usePayrollQuote(String(deferredAmount), termMonths, currentDate, {
    enabled: deferredAmount > 0,
  });
  const quoteReady = quote !== undefined && deferredAmount === amount && quote.term_months === termMonths;

  const maxAmount = quoteReady ? Number(quote.max_amount) : 0;
  const overMargin = quoteReady && !quote.fits_margin;
  const noMargin = quoteReady && Number(quote.margin_free) <= 0;
  const noDebtRoom = quoteReady && !quote.fits_debt_limit;
  const canSign = quoteReady && quote.fits_margin && quote.fits_debt_limit && amount > 0;

  const setAmount = (value: string) => setAmountText(formatMoney(value));

  return (
    <div className="grid gap-4">
      <p className="text-[13px] text-muted-foreground">
        <b className="font-semibold text-foreground">Exclusivo da profissão.</b> SELIC + 2 · a parcela sai do salário
        antes de cair no caixa
      </p>

      {/* Valor e prazo */}
      <div className="grid items-start gap-5 sm:grid-cols-2">
        <Field data-invalid={overMargin}>
          <FieldLabel htmlFor="payroll-amount">Valor</FieldLabel>
          <Input
            id="payroll-amount"
            fieldSize="xl"
            numeric
            inputMode="decimal"
            value={amountText}
            aria-invalid={overMargin}
            onChange={(event) => setAmount(event.target.value)}
          />
          {overMargin && !noMargin ? (
            <>
              <FieldError>
                Passa da margem: em {termMonths} meses cabe até {displayMoney(maxAmount)}.
              </FieldError>
              <Button
                variant="link"
                size="sm"
                className="justify-self-start"
                onClick={() => setAmount(toCentsString(String(maxAmount)))}
              >
                Usar o máximo, {displayMoney(maxAmount)}
              </Button>
            </>
          ) : (
            <FieldDescription>
              {quoteReady
                ? `Até ${displayMoney(maxAmount)} em ${termMonths} meses · o que cabe na margem livre`
                : "Calculando o que cabe na margem livre…"}
            </FieldDescription>
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

      {error && !quote ? (
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>Não deu para calcular a parcela</AlertTitle>
          <AlertDescription>A simulação não respondeu. O valor e o prazo continuam aí.</AlertDescription>
          <AlertAction>
            <Button size="sm" variant="outline" onClick={() => void refetch()}>
              <RefreshCw />
              Calcular de novo
            </Button>
          </AlertAction>
        </Alert>
      ) : (
        <>
          {/* Juro travado e a comparação com o comum */}
          <div className="flex flex-wrap items-center gap-2 rounded-lg bg-subtle px-3 py-2.5 text-[13px]">
            <span>Juro</span>
            {quoteReady ? (
              <>
                <b className="font-mono">{displayPercent(quote.monthly_rate)} ao mês</b>
                <span className="text-muted-foreground">
                  · {displayPercent(quote.annual_rate)} ao ano, travado no contrato
                  {quote.common_annual_rate !== null && ` · o comum seria ${displayPercent(quote.common_annual_rate)}`}
                </span>
              </>
            ) : (
              <span className="text-muted-foreground">Calculando…</span>
            )}
          </div>

          {/* O custo */}
          <div className="grid gap-4 sm:grid-cols-2">
            <Kpi
              label="Parcela mensal"
              value={quoteReady ? displayMoney(quote.installment) : "—"}
              note={
                quoteReady
                  ? `sai do salário · 1ª em ${displayDate(parseLocalDate(quote.first_installment_date))}, 30 dias depois da assinatura`
                  : "Calculando…"
              }
            />
            <Kpi
              label="Juro no prazo todo"
              value={quoteReady ? displayMoney(quote.total_interest) : "—"}
              note={
                quoteReady && quote.interest_saved !== null
                  ? `${displayMoney(quote.interest_saved)} a menos que no comum`
                  : undefined
              }
              tone={quoteReady && quote.interest_saved !== null ? "success" : "default"}
            />
          </div>

          {/* Margem consignável */}
          {quoteReady && <MarginBar quote={quote} />}

          {noMargin && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>Sem margem livre.</AlertTitle>
              <AlertDescription>
                As parcelas dos seus consignados já somam {displayMoney(quote.margin_used)}, os 35% do salário líquido.
                A margem volta a abrir quando um contrato terminar.
              </AlertDescription>
            </Alert>
          )}
          {noDebtRoom && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>Sem limite de dívida.</AlertTitle>
              <AlertDescription>
                O consignado usa o mesmo limite do empréstimo comum: a dívida pode crescer mais{" "}
                {displayMoney(quote.debt_limit_room)}, e este valor passa disso.
              </AlertDescription>
            </Alert>
          )}
        </>
      )}

      <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Info className="size-3.5" aria-hidden="true" />
        Usa o mesmo limite de dívida do empréstimo comum. A alavancagem entra na nota de risco, recalculada no fim de{" "}
        {displayMonthName(overview.rating.next_review)}.
      </span>

      {/* Ações */}
      <div className="flex justify-end gap-2">
        <Button variant="outline" disabled={!quoteReady} onClick={() => setListing(true)}>
          Ver as {termMonths} parcelas
        </Button>
        <Button disabled={!canSign} onClick={() => setReviewing(true)}>
          Revisar e assinar
        </Button>
      </div>

      {quoteReady && (
        <>
          <ReviewPayrollDialog open={reviewing} onOpenChange={setReviewing} quote={quote} />
          <InstallmentsDialog open={listing} onOpenChange={setListing} quote={quote} />
        </>
      )}
    </div>
  );
}

function MarginBar({ quote }: { quote: PayrollQuote }) {
  const margin = Number(quote.margin);
  const used = Number(quote.margin_used);
  const thisLoan = Math.min(Number(quote.installment), Math.max(margin - used, 0));
  const fractionOf = (part: number) => (margin > 0 ? part / margin : 0);

  return (
    <div className="grid gap-1.5 rounded-xl border p-4">
      <div className="flex justify-between gap-3 text-[13px]">
        <span className="inline-flex items-center gap-1 font-medium">
          Margem consignável <MetricHint metric={PAYROLL_MARGIN} />
        </span>
        <span className="font-mono text-muted-foreground">{displayMoney(margin)} por mês</span>
      </div>
      <StackedBar
        size="lg"
        segments={[
          { key: "used", fraction: fractionOf(used), color: "bg-primary" },
          { key: "loan", fraction: fractionOf(thisLoan), color: "bg-info-border" },
        ]}
      />
      <ul className="flex flex-wrap gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
        <li>
          usada <span className="font-mono">{displayMoney(used)}</span>
        </li>
        <li>
          este consignado <span className="font-mono">{displayMoney(quote.installment)}</span>
        </li>
        <li>
          livre <span className="font-mono">{displayMoney(quote.margin_free_after)}</span>
        </li>
      </ul>
    </div>
  );
}
