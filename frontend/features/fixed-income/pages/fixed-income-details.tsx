import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { differenceInCalendarDays } from "date-fns";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorPage } from "@/pages/error";
import { ErrorState } from "@/shared/components/error-state";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { cn, normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import {
  displayDate,
  displayMoney,
  displayPercent,
  displayRateLabel,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FixedIncomeOffer, FixedIncomeQuote } from "@/types";
import { InvestmentTicket } from "../components/investment-ticket";
import { useFixedIncomeAsset } from "../hooks/queries/useFixedIncomeAsset";
import { useFixedIncomeProjection } from "../hooks/queries/useFixedIncomeProjection";
import { INVESTMENT_TYPE_LABELS, RATE_KIND_LABELS } from "../lib/labels";

const NOT_FOUND = (
  <ErrorPage
    title="Essa oferta está indisponível"
    message="O catálogo pode ter sido atualizado. Consulte as ofertas atuais."
    actionLabel="Ver renda fixa"
    actionHref="/fixed-income"
  />
);

export default function FixedIncomeDetailPage() {
  usePageLabel("Renda fixa");
  const { id } = useParams<{ id: string }>();
  const { data: offer, isLoading, error, refetch } = useFixedIncomeAsset(id);
  const { data: simulation, error: stateError, refetch: refetchState } = useSimulationState();

  if (error?.status === 404) return NOT_FOUND;
  if (error || stateError) return <ErrorState title="Não deu para carregar esse título"
    description="Confira a conexão e tente novamente." error={error ?? stateError}
    onRetry={() => { void refetch(); void refetchState(); }} />;

  if (isLoading || !simulation?.current_date) {
    return <Skeleton className="h-96" />;
  }
  if (!offer || !id) return NOT_FOUND;
  if (offer.maturity_date <= simulation.current_date) return <ErrorPage code="410"
    title="Esse título já venceu" message="Consulte as ofertas disponíveis na data atual da partida."
    actionLabel="Ver renda fixa" actionHref="/fixed-income" />;

  return <FixedIncomeDetail key={id} id={id} offer={offer} today={simulation.current_date} />;
}

function FixedIncomeDetail({ id, offer, today }: { id: string; offer: FixedIncomeOffer; today: string }) {
  const [amountText, setAmountText] = useState(formatMoney("0"));
  const { data: quote, error, isLoading, refetch } = useFixedIncomeProjection(id, normalizeNumberString(amountText), today);
  const daysToRedeem = quote
    ? differenceInCalendarDays(parseLocalDate(quote.redemption_date), parseLocalDate(today))
    : null;

  const metrics = [
    { label: "Rentabilidade", value: displayRateLabel(offer.rate_index, offer.interest_rate) },
    ...(offer.effective_annual_rate === null
      ? []
      : [
          {
            label: "Equivale hoje",
            value: `${displayPercent(offer.effective_annual_rate)} a.a.`,
            detail:
              offer.rate_index !== "Prefixado"
                ? `${offer.rate_index} ${displayPercent(offer.index_rate)} · Banco Central`
                : null,
          },
        ]),
    {
      label: "Vencimento",
      value: displayDate(parseLocalDate(offer.maturity_date)),
      detail: daysToRedeem !== null ? `em ${daysToRedeem} dias` : null,
    },
    {
      label: "IR nesse prazo",
      value: offer.tax_exempt ? "Isento" : displayPercent(offer.income_tax_rate_at_maturity),
      detail: offer.tax_exempt ? "LCI e LCA não pagam IR" : "tabela regressiva",
    },
  ];

  return (
    <>
      {/* Cabeçalho */}
      <header className="grid gap-1.5">
        <Button
          variant="link"
          size="sm"
          nativeButton={false}
          render={<Link to="/fixed-income" />}
          className="justify-self-start"
        >
          <ArrowLeft />
          Renda fixa
        </Button>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-[26px] font-bold">{offer.name}</h1>
          <Badge variant="secondary">
            {INVESTMENT_TYPE_LABELS[offer.investment_type]} · {RATE_KIND_LABELS[offer.rate_index]}
          </Badge>
          <span className="text-muted-foreground">emitido por {offer.issuer}</span>
        </div>
      </header>

      {/* Os números do título */}
      <Card>
        <CardContent>
          <div
            className={cn(
              "grid gap-4 sm:grid-cols-2 lg:gap-0",
              metrics.length === 4 ? "lg:grid-cols-4" : "lg:grid-cols-3",
            )}
          >
            {metrics.map((m) => (
              <div key={m.label} className="grid gap-0.5 lg:border-l lg:pl-5 lg:first:border-l-0 lg:first:pl-0">
                <span className="text-xs font-medium text-muted-foreground">{m.label}</span>
                <span className="font-mono text-lg font-semibold">{m.value}</span>
                {m.detail && <span className="text-xs text-muted-foreground">{m.detail}</span>}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        {error && <ErrorState title="Não deu para conferir o investimento" description="Atualize a cotação antes de investir."
          error={error} onRetry={() => void refetch()} />}
        {isLoading && <Skeleton className="h-64" />}
        <div className="grid gap-5">
          {quote && <Projection quote={quote} />}
          {quote && daysToRedeem !== null && !offer.tax_exempt && <TaxSteps quote={quote} days={daysToRedeem} />}
        </div>
        {quote && !error && (
          <InvestmentTicket assetId={id} amountText={amountText} onAmountChange={setAmountText} quote={quote} />
        )}
      </div>
    </>
  );
}

/** Aplicado → rendimento → IR → resgate, numa barra só. */
function Projection({ quote }: { quote: FixedIncomeQuote }) {
  const { gross_amount, gross_return, gross_return_pct, income_tax, net_amount, net_return_pct } = quote;
  // A partida pode esconder a projeção: sem os números o bloco não existe
  if (
    gross_amount === null ||
    gross_return === null ||
    gross_return_pct === null ||
    income_tax === null ||
    net_amount === null ||
    net_return_pct === null
  ) {
    return null;
  }

  const hasAmount = Number(quote.amount) > 0;
  const gross = Number(gross_amount) || 1;
  const parts = [
    {
      key: "applied",
      label: "Aplicado",
      value: displayMoney(quote.amount),
      detail: null,
      share: Number(quote.amount) / gross,
      className: "bg-input",
    },
    {
      key: "yield",
      label: "Rendimento bruto",
      value: `+${displayMoney(gross_return)}`,
      detail: `+${displayPercent(gross_return_pct)}`,
      share: (Number(gross_return) - Number(income_tax)) / gross,
      className: "bg-success",
    },
    {
      key: "tax",
      label: "IR",
      value: `−${displayMoney(income_tax)}`,
      detail: `alíquota ${displayPercent(quote.income_tax_rate, 1)}`,
      share: Number(income_tax) / gross,
      className: "bg-[repeating-linear-gradient(135deg,var(--destructive)_0_3px,transparent_3px_6px)]",
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {hasAmount
            ? `Quanto ${displayMoney(quote.amount)} viram no vencimento`
            : "Quanto o dinheiro rende até o vencimento"}
        </CardTitle>
        <CardDescription>
          Projeção com a taxa de hoje. Se o índice mudar durante a partida, o resultado muda junto.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          {hasAmount && (
            <div className="flex h-7 gap-0.5 overflow-hidden rounded-lg">
              {parts.map((p) => (
                <span key={p.key} className={p.className} style={{ width: `${Math.max(p.share, 0) * 100}%` }} />
              ))}
            </div>
          )}
          <dl className="grid gap-3 sm:grid-cols-4">
            {parts.map((p) => (
              <div key={p.key} className="grid gap-0.5">
                <dt className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <span className={cn("size-2.5 rounded-sm", p.className)} aria-hidden="true" />
                  {p.label}
                </dt>
                <dd className="font-mono text-[13px] font-semibold">{hasAmount ? p.value : "—"}</dd>
                {hasAmount && p.detail && <dd className="font-mono text-xs text-muted-foreground">{p.detail}</dd>}
              </div>
            ))}
            <div className="grid gap-0.5">
              <dt className="text-xs text-muted-foreground">Resgate líquido</dt>
              <dd className="font-mono text-[13px] font-semibold">
                {hasAmount ? displayMoney(net_amount) : `+${displayPercent(net_return_pct)}`}
              </dd>
              {hasAmount && (
                <dd className="font-mono text-xs text-muted-foreground">+{displayPercent(net_return_pct)}</dd>
              )}
            </div>
          </dl>
        </div>
      </CardContent>
    </Card>
  );
}

/** A tabela regressiva em degraus, com a faixa do prazo deste título em destaque. */
function TaxSteps({ quote, days }: { quote: FixedIncomeQuote; days: number }) {
  const brackets = quote.income_tax_brackets;
  const current = brackets.findIndex((b) => b.max_days === null || days <= b.max_days);

  return (
    <Card>
      <CardHeader>
        <CardTitle>IR cai com o tempo</CardTitle>
        <CardDescription>Quanto mais tempo o dinheiro fica, menor a alíquota sobre o rendimento.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-1.5">
          {brackets.map((b, i) => {
            const from = i === 0 ? 0 : (brackets[i - 1].max_days ?? 0) + 1;
            const label =
              b.max_days === null
                ? `acima de ${from - 1} dias`
                : i === 0
                  ? `até ${b.max_days} dias`
                  : `${from} a ${b.max_days}`;
            const active = i === current;
            return (
              <div
                key={label}
                className={cn(
                  "grid flex-1 gap-0.5 rounded-lg p-3",
                  active ? "bg-foreground text-primary-foreground" : "bg-background",
                )}
              >
                <span className={cn("text-xs", active ? "text-sidebar-foreground" : "text-muted-foreground")}>
                  {label}
                </span>
                <span className="font-mono font-semibold">{displayPercent(b.rate, 1)}</span>
                {active && <span className="text-xs text-sidebar-foreground">você resgata em {days} dias</span>}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
