import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { differenceInCalendarDays } from "date-fns";
import { CircleCheck, Info, TriangleAlert } from "lucide-react";
import { useTradeLock } from "@/shared/hooks/useTradeLock";
import { TradeLockNotice } from "@/shared/components/trade-lock-notice";
import { DailyLiquidityBadge } from "@/shared/components/daily-liquidity-badge";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { cn, normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import {
  displayDate,
  displayMoney,
  displayPercent,
  displayRateLabel,
  parseLocalDate,
  toCentsString,
} from "@/shared/lib/utils/display";
import type { FixedIncomeOffer, FixedIncomePosition, FixedIncomeRedemptionQuote } from "@/types";
import { useRedeemFixedIncome } from "@/shared/hooks/mutations/useRedeemFixedIncome";
import { useFixedIncomeRedemption } from "../hooks/queries/useFixedIncomeRedemption";

const SHORTCUTS = [
  { label: "R$ 1 mil", value: "1000" },
  { label: "R$ 5 mil", value: "5000" },
];

type RedemptionTicketProps = {
  assetId: string;
  offer: FixedIncomeOffer;
  /** A posição do jogador neste título; sem ela não há o que resgatar */
  position: FixedIncomePosition | undefined;
  today: string;
  /** A oferta saiu do catálogo: quem aplicou segue resgatando */
  leftCatalogOn: string | null;
  /** O CDB de 100% do CDI, sempre aberto, para quem não pode mais aplicar nesta oferta */
  permanentCdbId: string | undefined;
  onInvest: () => void;
};

/** Aba "Resgatar" da boleta: quanto cai no caixa, o que sai do título e os impostos. */
export function RedemptionTicket({
  assetId,
  offer,
  position,
  today,
  leftCatalogOn,
  permanentCdbId,
  onInvest,
}: RedemptionTicketProps) {
  const redeem = useRedeemFixedIncome(assetId);
  // O que a confirmação mostra é o que o resgate fez, guardado no momento do clique
  const [done, setDone] = useState<FixedIncomeRedemptionQuote | null>(null);

  if (!offer.daily_liquidity) return <WithoutLiquidity offer={offer} />;

  if (done) {
    return (
      <Confirmation
        quote={done}
        onAgain={() => {
          setDone(null);
          redeem.reset();
        }}
      />
    );
  }

  if (!position) {
    return (
      <div className="grid gap-3 text-[13px]">
        {leftCatalogOn && <LeftCatalog date={leftCatalogOn} offer={offer} />}
        <b className="font-semibold">Você não tem aplicação neste título</b>
        <span className="text-muted-foreground">
          Quando investir aqui, o dinheiro volta ao caixa em qualquer pregão.
        </span>
        {!leftCatalogOn && (
          <Button variant="outline" onClick={onInvest}>
            Investir
          </Button>
        )}
        {leftCatalogOn && permanentCdbId && <PermanentCdbLink id={permanentCdbId} />}
      </div>
    );
  }

  return (
    <RedemptionForm
      assetId={assetId}
      offer={offer}
      today={today}
      leftCatalogOn={leftCatalogOn}
      permanentCdbId={permanentCdbId}
      redeem={redeem}
      onDone={setDone}
    />
  );
}

type RedemptionFormProps = Omit<RedemptionTicketProps, "position" | "onInvest"> & {
  redeem: ReturnType<typeof useRedeemFixedIncome>;
  onDone: (quote: FixedIncomeRedemptionQuote) => void;
};

function RedemptionForm({ assetId, offer, today, leftCatalogOn, permanentCdbId, redeem, onDone }: RedemptionFormProps) {
  const [amountText, setAmountText] = useState(formatMoney("0"));
  const [touched, setTouched] = useState(false);
  const amount = Number(normalizeNumberString(amountText)) || 0;
  const { data: quote, error, isLoading, refetch } = useFixedIncomeRedemption(
    assetId,
    normalizeNumberString(amountText),
    today,
    true,
  );
  // Com o automático ligado a boleta fica só para leitura
  const tradeLock = useTradeLock();
  const locked = tradeLock !== null;

  const max = quote ? Number(quote.max_amount) : 0;
  const zero = amount <= 0;
  const over = quote !== undefined && amount > max;
  const invalid = touched && (zero || over);
  // Só vale a cotação do valor que está na tela; a anterior fica de pé até a nova chegar
  const current = quote && !zero && !over && Number(quote.amount) === amount ? quote : undefined;

  const setAmount = (value: string) => {
    setTouched(true);
    setAmountText(formatMoney(toCentsString(value)));
  };

  const submit = () => {
    if (!current) return;
    redeem.mutate({ amount: normalizeNumberString(amountText) }, { onSuccess: () => onDone(current) });
  };

  const iof = current ? Number(current.iof) : 0;
  const rows = [
    { label: "Sai do título", value: current && displayMoney(current.gross_amount ?? 0) },
    {
      label: current?.full ? "Rendimento" : "Rendimento nessa parte",
      value: current && `+${displayMoney(current.yield_amount ?? 0)}`,
      tone: "up" as const,
    },
    ...(iof > 0 && current
      ? [
          {
            label: `IOF · ${displayPercent(current.iof_rate, 0)} (${current.days_held} ${current.days_held === 1 ? "dia" : "dias"} aplicado)`,
            value: `−${displayMoney(current.iof ?? 0)}`,
            tone: "down" as const,
          },
          {
            label: `IR · ${displayPercent(current.income_tax_rate, 1)} sobre o que sobra`,
            value: `−${displayMoney(current.income_tax ?? 0)}`,
            tone: "down" as const,
          },
        ]
      : [
          {
            label: current
              ? `IR · ${displayPercent(current.income_tax_rate, 1)} (${current.days_held} ${current.days_held === 1 ? "dia" : "dias"} aplicado)`
              : "IR",
            value: current && `−${displayMoney(current.income_tax ?? 0)}`,
            tone: "down" as const,
          },
        ]),
  ];

  const notice = current && noticeFor(current, today);

  return (
    <>
      {tradeLock && <TradeLockNotice lock={tradeLock} />}
      <div inert={locked} className={cn("grid gap-4", locked && "opacity-55")}>
        {leftCatalogOn && <LeftCatalog date={leftCatalogOn} offer={offer} />}

        <Field data-invalid={invalid}>
          <FieldLabel htmlFor="redeem-amount">Quanto quer receber no caixa</FieldLabel>
          <Input
            id="redeem-amount"
            fieldSize="xl"
            numeric
            inputMode="decimal"
            value={amountText}
            aria-invalid={invalid}
            onChange={(e) => {
              setTouched(true);
              setAmountText(formatMoney(e.target.value));
            }}
          />
          {invalid && (
            <FieldError>
              {zero
                ? "Digite quanto quer receber."
                : `Dá pra receber até ${displayMoney(max)} hoje, já descontado o IR. Use “Tudo” pra resgatar tudo.`}
            </FieldError>
          )}
        </Field>

        <div className="grid grid-cols-4 gap-1.5">
          {SHORTCUTS.map((s) => (
            <Button key={s.label} variant="outline" size="sm" onClick={() => setAmount(s.value)}>
              {s.label}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            disabled={!quote}
            onClick={() => setAmount(String(Math.floor(max * 50) / 100))}
          >
            Metade
          </Button>
          <Button variant="outline" size="sm" disabled={!quote} onClick={() => setAmount(quote?.max_amount ?? "0")}>
            Tudo
          </Button>
        </div>

        {error && !quote ? (
          <div className="grid gap-1.5 rounded-lg border border-border bg-subtle px-3 py-2.5 text-[13px]">
            <b className="flex items-center gap-1.5 font-semibold">
              <TriangleAlert className="size-4 text-destructive" />
              Não deu para calcular o resgate
            </b>
            <span className="text-muted-foreground">O valor do título não mudou. Tente de novo antes de resgatar.</span>
            <Button variant="outline" size="sm" className="justify-self-start" onClick={() => void refetch()}>
              Tentar de novo
            </Button>
          </div>
        ) : (
          <dl className="grid gap-1.5 border-t border-muted pt-3 text-[13px]">
            {isLoading ? (
              <>
                {Array.from({ length: 5 }, (_, i) => (
                  <div key={i} className="flex justify-between gap-3">
                    <Skeleton className="h-4 w-28" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                ))}
              </>
            ) : (
              <>
                {rows.map((row) => (
                  <Row key={row.label} label={row.label} tone={row.tone}>
                    {row.value ?? "—"}
                  </Row>
                ))}
                <div className="flex justify-between gap-3 border-t border-muted pt-2">
                  <dt className="font-semibold">Cai no caixa hoje</dt>
                  <dd className={cn("font-mono text-[15px] font-semibold", current && "text-success")}>
                    {current ? displayMoney(current.net_amount ?? 0) : "—"}
                  </dd>
                </div>
                <Row label="Caixa depois">{current ? displayMoney(current.cash_after ?? 0) : "—"}</Row>
                {current && !current.full && (
                  <Row label="Continua aplicado">{displayMoney(current.remaining ?? 0)}</Row>
                )}
              </>
            )}
          </dl>
        )}

        {current?.full && (
          <span className="text-[13px] text-muted-foreground">
            O título sai da carteira. Dá pra voltar a investir nele depois, mas o prazo do IR recomeça.
          </span>
        )}

        {notice && (
          <div className="flex items-start gap-2 rounded-lg bg-info-soft px-3 py-2.5 text-xs text-info">
            <Info className="mt-px size-4 shrink-0" />
            <span>{notice}</span>
          </div>
        )}

        {leftCatalogOn && permanentCdbId && <PermanentCdbLink id={permanentCdbId} />}

        <Button
          size="lg"
          variant="dark"
          disabled={locked || !current || redeem.isPending}
          onClick={submit}
        >
          {redeem.isPending && <Spinner />}
          {redeem.isPending
            ? "Resgatando…"
            : !current
              ? "Resgatar"
              : current.full
                ? `Resgatar tudo · ${displayMoney(current.net_amount ?? 0)} no caixa`
                : `Receber ${displayMoney(current.net_amount ?? 0)} no caixa`}
        </Button>
      </div>
    </>
  );
}

/** O aviso azul: o IOF dos primeiros 30 dias ou a próxima queda do IR, o que vier primeiro. */
function noticeFor(quote: FixedIncomeRedemptionQuote, today: string): ReactNode {
  const daysUntil = (iso: string) => differenceInCalendarDays(parseLocalDate(iso), parseLocalDate(today));
  if (quote.iof_free_date && Number(quote.iof_rate) > 0) {
    const days = daysUntil(quote.iof_free_date);
    return (
      <>
        Nos primeiros 30 dias o IOF leva parte do rendimento: {displayPercent(quote.iof_rate, 0)} hoje, zero a partir
        de <b>{displayDate(parseLocalDate(quote.iof_free_date))}</b> (daqui a {days} {days === 1 ? "dia" : "dias"}).
      </>
    );
  }
  if (quote.next_tax_drop && !quote.full) {
    const days = daysUntil(quote.next_tax_drop.on);
    return (
      <>
        Em <b>{displayDate(parseLocalDate(quote.next_tax_drop.on))}</b> (daqui a {days} {days === 1 ? "dia" : "dias"}) o
        IR cai para <b>{displayPercent(quote.next_tax_drop.rate, 0)}</b>. Resgatar só o que precisa agora deixa o resto
        pagar menos.
      </>
    );
  }
  return null;
}

function Row({ label, tone, children }: { label: string; tone?: "up" | "down"; children: ReactNode }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={cn("font-mono", tone === "up" && "text-success", tone === "down" && "text-destructive")}>
        {children}
      </dd>
    </div>
  );
}

function Confirmation({ quote, onAgain }: { quote: FixedIncomeRedemptionQuote; onAgain: () => void }) {
  const taxes = Number(quote.iof) + Number(quote.income_tax);
  const taxName = Number(quote.iof) > 0 ? "IOF e IR" : "IR";
  return (
    <div className="grid gap-3">
      <div className="grid gap-1.5 text-[13px]">
        <b className="flex items-center gap-1.5 text-[15px] font-semibold text-success">
          <CircleCheck className="size-4" />
          {displayMoney(quote.net_amount ?? 0)} no caixa
        </b>
        <span className="text-muted-foreground">
          Saíram {displayMoney(quote.gross_amount ?? 0)} do título; {displayMoney(taxes)} foram de {taxName}.{" "}
          {quote.full ? "O título saiu da carteira." : `Continuam aplicados ${displayMoney(quote.remaining ?? 0)}.`}
        </span>
        <Link to="/portfolio" className="font-medium text-primary hover:text-primary-hover">
          Ver na carteira →
        </Link>
      </div>
      <Button variant="outline" onClick={onAgain}>
        Resgatar mais
      </Button>
    </div>
  );
}

function WithoutLiquidity({ offer }: { offer: FixedIncomeOffer }) {
  return (
    <div className="grid gap-3 text-[13px]">
      <b className="flex items-center gap-1.5 font-semibold">
        <Info className="size-4 text-muted-foreground" />
        Este título só volta ao caixa no vencimento
      </b>
      <span className="text-muted-foreground">
        O {offer.name} paga {displayRateLabel(offer.rate_index, offer.interest_rate)} em troca de travar o dinheiro até{" "}
        <b className="font-mono font-semibold text-foreground">{displayDate(parseLocalDate(offer.maturity_date))}</b>.
        Nesse dia, o valor cai no caixa sozinho.
      </span>
      <span className="text-muted-foreground">
        Pra ter dinheiro que sai em qualquer dia, procure os títulos com{" "}
        <DailyLiquidityBadge size="sm">liquidez diária</DailyLiquidityBadge>.
      </span>
      <Button
        variant="outline"
        nativeButton={false}
        render={<Link to="/fixed-income?liquidity=daily" />}
      >
        Ver títulos com liquidez diária
      </Button>
    </div>
  );
}

function LeftCatalog({ date, offer }: { date: string; offer: FixedIncomeOffer }) {
  return (
    <div className="grid gap-1 text-[13px]">
      <b className="font-semibold">A oferta saiu do catálogo em {displayDate(parseLocalDate(date))}</b>
      <span className="text-muted-foreground">
        Ninguém aplica mais nela. O que você já tem continua rendendo{" "}
        {displayRateLabel(offer.rate_index, offer.interest_rate)} e sai em qualquer dia.
      </span>
    </div>
  );
}

function PermanentCdbLink({ id }: { id: string }) {
  return (
    <Link to={`/fixed-income/${id}`} className="text-[13px] font-medium text-primary hover:text-primary-hover">
      Ver o CDB de 100% do CDI, sempre aberto →
    </Link>
  );
}
