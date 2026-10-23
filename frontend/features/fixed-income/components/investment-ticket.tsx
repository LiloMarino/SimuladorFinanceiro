import { useState } from "react";
import { Link } from "react-router-dom";
import { addDays, format } from "date-fns";
import { CircleCheck } from "lucide-react";
import { AutomaticLock } from "@/shared/components/automatic-lock";
import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { cn } from "@/shared/lib/utils";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Progress } from "@/shared/components/ui/progress";
import { Spinner } from "@/shared/components/ui/spinner";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import {
  displayDate,
  displayMoney,
  displayMoneyWhole,
  displayRateLabel,
  parseLocalDate,
  toCentsString,
} from "@/shared/lib/utils/display";
import type { FixedIncomeOffer, FixedIncomeQuote } from "@/types";
import { useBuyFixedIncome } from "../hooks/mutations/useBuyFixedIncome";

const SHORTCUTS = [
  { label: "R$ 1 mil", value: "1000" },
  { label: "R$ 5 mil", value: "5000" },
  { label: "R$ 10 mil", value: "10000" },
];

type InvestmentTicketProps = {
  assetId: string;
  offer: FixedIncomeOffer;
  amountText: string;
  onAmountChange: (text: string) => void;
  quote: FixedIncomeQuote;
};

/** Aba "Investir" da boleta: valor, caixa antes e depois e o que o título devolve. */
export function InvestmentTicket({ assetId, offer, amountText, onAmountChange, quote }: InvestmentTicketProps) {
  const [touched, setTouched] = useState(false);
  const amount = Number(normalizeNumberString(amountText)) || 0;
  const overCash = amount > Number(quote.cash_before);
  const zero = amount <= 0;
  const cap = offer.player_cap === null ? null : Number(offer.player_cap);
  const applied = Number(quote.cap_used ?? 0);
  // Quanto ainda cabe no teto da oferta; sem teto, cabe tudo
  const room = cap === null ? Infinity : Math.max(cap - applied, 0);
  const overCap = amount > room;

  const invest = useBuyFixedIncome(assetId);
  // Com o automático ligado a boleta fica só para leitura
  const locked = !!useMyStrategy().data?.active;

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
    );
  }

  const invalid = touched && (zero || overCap || overCash);
  const errorText = zero
    ? "Digite quanto quer investir."
    : overCap
      ? `Seu teto nesta oferta é ${displayMoney(cap ?? 0)} e você já aplicou ${displayMoney(applied)}: cabem mais ${displayMoney(room)}.`
      : `Você tem ${displayMoney(quote.cash_before)} em caixa.`;
  // Sem o teto, o atalho "Tudo" leva ao caixa; com ele, "Máx" leva ao que cabe
  const maxLabel = cap === null ? "Tudo" : "Máx";

  return (
    <>
      {locked && <AutomaticLock />}
      <div inert={locked} className={cn("grid gap-4", locked && "opacity-55")}>
        {cap !== null && offer.offered_until && (
          <RareOfferCap cap={cap} applied={applied} room={room} offeredUntil={offer.offered_until} />
        )}

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
          {invalid && <FieldError>{errorText}</FieldError>}
        </Field>

        <div className="grid grid-cols-3 gap-1.5">
          {SHORTCUTS.map((s) => (
            <Button key={s.label} variant="outline" size="sm" onClick={() => addToAmount(s.value)}>
              {s.label}
            </Button>
          ))}
          <Button variant="outline" size="sm" onClick={() => setAmount(quote.max_amount)}>
            {maxLabel}
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
            <dd className="font-mono">{overCash || overCap ? "—" : displayMoney(quote.cash_after)}</dd>
          </div>
          {offer.daily_liquidity ? (
            <div className="flex justify-between gap-3">
              <dt className="text-muted-foreground">Rende</dt>
              <dd className="text-right font-mono">
                {displayRateLabel(offer.rate_index, offer.interest_rate)} até você resgatar
              </dd>
            </div>
          ) : (
            quote.net_amount !== null && (
              <div className="flex justify-between">
                <dt className="text-muted-foreground">
                  Resgate líquido em {displayDate(parseLocalDate(quote.redemption_date))}
                </dt>
                <dd className="font-mono font-semibold">{zero ? "—" : displayMoney(quote.net_amount)}</dd>
              </div>
            )
          )}
        </dl>

        <Button
          size="lg"
          variant="success"
          disabled={locked || zero || overCash || overCap || invest.isPending}
          onClick={() => invest.mutate({ quantity: normalizeNumberString(amountText) })}
        >
          {invest.isPending && <Spinner />}
          {invest.isPending ? "Investindo…" : invalid && !zero ? "Investir" : `Investir ${displayMoney(amount)}`}
        </Button>
      </div>
    </>
  );
}

/** Teto por jogador da oferta rara: quanto já foi aplicado, quanto cabe e até quando fica no catálogo. */
function RareOfferCap({
  cap,
  applied,
  room,
  offeredUntil,
}: {
  cap: number;
  applied: number;
  room: number;
  offeredUntil: string;
}) {
  const until = parseLocalDate(offeredUntil);
  return (
    <div className="grid gap-2 rounded-lg border border-warning/30 bg-warning-soft/40 px-3 py-2.5 text-xs">
      <div className="flex items-baseline justify-between gap-3">
        <b className="font-semibold text-warning">Oferta rara · teto por jogador</b>
        <span className="font-mono font-medium text-warning">até {displayDate(until)}</span>
      </div>
      <Progress
        value={cap > 0 ? Math.min(applied / cap, 1) * 100 : 0}
        size="sm"
        indicatorTone="warning"
        aria-label="Quanto do teto da oferta você já aplicou"
      />
      <span>
        Você já aplicou <b className="font-mono">{displayMoneyWhole(applied)}</b> do seu teto de{" "}
        <b className="font-mono">{displayMoneyWhole(cap)}</b>: dá pra aplicar mais{" "}
        <b className="font-mono">{displayMoneyWhole(room)}</b>. Some quando o catálogo virar, em{" "}
        {format(addDays(until, 1), "dd/MM")}.
      </span>
    </div>
  );
}
