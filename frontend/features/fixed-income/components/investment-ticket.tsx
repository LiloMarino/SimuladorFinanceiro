import { useState } from "react";
import { Link } from "react-router-dom";
import { CircleCheck } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import { displayDate, displayMoney, parseLocalDate, toCentsString } from "@/shared/lib/utils/display";
import type { FixedIncomeQuote } from "@/types";
import { useBuyFixedIncome } from "../hooks/mutations/useBuyFixedIncome";

const SHORTCUTS = [
  { label: "R$ 1 mil", value: "1000" },
  { label: "R$ 5 mil", value: "5000" },
  { label: "R$ 10 mil", value: "10000" },
];

type InvestmentTicketProps = {
  assetId: string;
  amountText: string;
  onAmountChange: (text: string) => void;
  quote: FixedIncomeQuote;
};

/** Boleta da renda fixa: valor, caixa antes e depois e o resgate líquido no vencimento. */
export function InvestmentTicket({ assetId, amountText, onAmountChange, quote }: InvestmentTicketProps) {
  const [touched, setTouched] = useState(false);
  const amount = Number(normalizeNumberString(amountText)) || 0;
  const overCash = amount > Number(quote.cash_before);
  const zero = amount <= 0;

  const invest = useBuyFixedIncome(assetId);

  const setAmount = (value: string) => {
    setTouched(true);
    onAmountChange(formatMoney(toCentsString(value)));
  };

  // O atalho soma ao valor digitado; a conta fecha em centavos inteiros.
  const addToAmount = (value: string) => {
    setTouched(true);
    onAmountChange(formatMoney(String(Math.round(amount * 100) + Number(value) * 100)));
  };

  if (invest.isSuccess) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Investir</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            <Alert variant="success">
              <CircleCheck />
              <AlertTitle>{displayMoney(amount)} aplicados</AlertTitle>
              <AlertDescription>
                <Link to="/portfolio" className="font-medium text-primary hover:text-primary-hover">
                  Ver na carteira →
                </Link>
              </AlertDescription>
            </Alert>
            <Button
              variant="outline"
              onClick={() => {
                invest.reset();
                onAmountChange(formatMoney("0"));
                setTouched(false);
              }}
            >
              Investir mais
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const invalid = touched && (zero || overCash);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Investir</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <Field data-invalid={invalid}>
            <FieldLabel htmlFor="invest-amount">Quanto investir</FieldLabel>
            <Input
              id="invest-amount"
              fieldSize="xl"
              numeric
              inputMode="decimal"
              value={amountText}
              aria-invalid={invalid}
              onChange={(e) => {
                setTouched(true);
                onAmountChange(formatMoney(e.target.value));
              }}
            />
            {invalid && (
              <FieldError>
                {zero ? "Digite quanto quer investir." : `Você tem ${displayMoney(quote.cash_before)} em caixa.`}
              </FieldError>
            )}
          </Field>

          <div className="grid grid-cols-3 gap-1.5">
            {SHORTCUTS.map((s) => (
              <Button key={s.label} variant="outline" size="sm" onClick={() => addToAmount(s.value)}>
                {s.label}
              </Button>
            ))}
            <Button variant="outline" size="sm" onClick={() => setAmount(quote.max_amount)}>
              Tudo
            </Button>
            <Button variant="outline" size="sm" onClick={() => setAmount("0")}>
              Limpar
            </Button>
          </div>

          <dl className="grid gap-1.5 border-t border-muted pt-3 text-[13px]">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Caixa agora</dt>
              <dd className="font-mono">{displayMoney(quote.cash_before)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Caixa depois</dt>
              <dd className="font-mono">{overCash ? "—" : displayMoney(quote.cash_after)}</dd>
            </div>
            {quote.net_amount !== null && (
              <div className="flex justify-between">
                <dt className="text-muted-foreground">
                  Resgate líquido em {displayDate(parseLocalDate(quote.redemption_date))}
                </dt>
                <dd className="font-mono font-semibold">{zero ? "—" : displayMoney(quote.net_amount)}</dd>
              </div>
            )}
          </dl>

          <Button
            size="lg"
            variant="success"
            disabled={zero || overCash || invest.isPending}
            onClick={() => invest.mutate({ quantity: normalizeNumberString(amountText) })}
          >
            {invest.isPending && <Spinner />}
            {invest.isPending ? "Investindo…" : `Investir ${displayMoney(amount)}`}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
