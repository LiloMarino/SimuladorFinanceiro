import { useState, type ReactNode } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { addDays, differenceInCalendarDays } from "date-fns";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorPage } from "@/pages/error";
import { DailyLiquidityBadge } from "@/shared/components/daily-liquidity-badge";
import { ErrorState } from "@/shared/components/error-state";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { cn, normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney } from "@/shared/lib/utils/format";
import {
  displayDate,
  displayMoney,
  displayPercent,
  displayRateLabel,
  displaySignedMoney,
  displaySignedPercent,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FixedIncomeOffer, FixedIncomePosition, FixedIncomeQuote } from "@/types";
import { InvestmentTicket } from "../components/investment-ticket";
import { RedemptionTicket } from "../components/redemption-ticket";
import { useFixedIncomeAsset } from "../hooks/queries/useFixedIncomeAsset";
import { useFixedIncomeAssets } from "../hooks/queries/useFixedIncomeAssets";
import { useFixedIncomeProjection } from "../hooks/queries/useFixedIncomeProjection";
import { useFixedIncomeRedemption } from "../hooks/queries/useFixedIncomeRedemption";
import { isPermanentCdb, isRareOffer } from "../lib/daily-liquidity";
import { INVESTMENT_TYPE_LABELS, RATE_KIND_LABELS, timeToMaturity } from "../lib/labels";

const NOT_FOUND = (
  <ErrorPage
    title="Essa oferta está indisponível"
    message="O catálogo pode ter sido atualizado. Consulte as ofertas atuais."
    actionLabel="Ver renda fixa"
    actionHref="/fixed-income"
  />
);

type Metric = { label: string; value: string; detail?: string | null; tone?: "success" };

export default function FixedIncomeDetailPage() {
  usePageLabel("Renda fixa");
  const { id } = useParams<{ id: string }>();
  const { data: offer, isLoading, error, refetch } = useFixedIncomeAsset(id);
  const { data: simulation, error: stateError, refetch: refetchState } = useSimulationState();

  if (error?.status === 404) return NOT_FOUND;
  if (error || stateError)
    return (
      <ErrorState
        title="Não deu para carregar esse título"
        description="Confira a conexão e tente novamente."
        error={error ?? stateError}
        onRetry={() => {
          void refetch();
          void refetchState();
        }}
      />
    );

  if (isLoading || !simulation?.current_date) {
    return <Skeleton className="h-96" />;
  }
  if (!offer || !id) return NOT_FOUND;
  if (offer.maturity_date <= simulation.current_date)
    return (
      <ErrorPage
        code="410"
        title="Esse título já venceu"
        message="Consulte as ofertas disponíveis na data atual da partida."
        actionLabel="Ver renda fixa"
        actionHref="/fixed-income"
      />
    );

  return <FixedIncomeDetail key={id} id={id} offer={offer} today={simulation.current_date} />;
}

function FixedIncomeDetail({ id, offer, today }: { id: string; offer: FixedIncomeOffer; today: string }) {
  const [searchParams] = useSearchParams();
  const [tab, setTab] = useState<"invest" | "redeem">(searchParams.get("tab") === "redeem" ? "redeem" : "invest");
  const [amountText, setAmountText] = useState(formatMoney("0"));
  const {
    data: quote,
    error,
    isLoading,
    refetch,
  } = useFixedIncomeProjection(id, normalizeNumberString(amountText), today);
  const { data: offers } = useFixedIncomeAssets();
  const { data: portfolio } = usePortfolio();
  const position = portfolio?.fixed_income.find((p) => p.asset.asset_uuid === id);
  const daysToRedeem = quote
    ? differenceInCalendarDays(parseLocalDate(quote.redemption_date), parseLocalDate(today))
    : null;

  const liquid = offer.daily_liquidity;
  // A oferta rara some do catálogo no fim do mês: quem aplicou segue resgatando, ninguém aplica mais
  const leftCatalogOn =
    offer.offered_until && today > offer.offered_until ? displayIsoNextDay(offer.offered_until) : null;
  const activeTab = leftCatalogOn ? "redeem" : tab;
  const heldDays = position
    ? differenceInCalendarDays(parseLocalDate(today), parseLocalDate(position.first_applied_date))
    : 0;
  const bracketIndex = quote?.income_tax_brackets.findIndex((b) => b.max_days === null || heldDays <= b.max_days) ?? -1;
  const taxToday = quote && bracketIndex >= 0 ? quote.income_tax_brackets[bracketIndex].rate : null;

  const metrics: Metric[] = [
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
    ...(liquid
      ? [{ label: "Resgate", value: "Qualquer dia", detail: "pelo valor do dia", tone: "success" as const }]
      : []),
    {
      label: "Vencimento",
      value: displayDate(parseLocalDate(offer.maturity_date)),
      detail: daysToRedeem !== null ? `em ${daysToRedeem.toLocaleString("pt-BR")} dias` : null,
    },
    liquid
      ? {
          label: "IR se resgatar hoje",
          value: taxToday === null ? "—" : displayPercent(taxToday),
          detail: position ? `aplicado há ${heldDays} dias` : "dinheiro novo começa aqui",
        }
      : {
          label: "IR nesse prazo",
          value: offer.tax_exempt ? "Isento" : displayPercent(offer.income_tax_rate_at_maturity),
          detail: offer.tax_exempt ? "LCI e LCA não pagam IR" : "tabela regressiva",
        },
  ];

  const permanentCdbId = offers?.find(isPermanentCdb)?.asset_uuid;

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
          {liquid && (
            <DailyLiquidityBadge>
              Liquidez diária · {isRareOffer(offer) ? "oferta rara" : "sempre disponível"}
            </DailyLiquidityBadge>
          )}
          <span className="text-muted-foreground">emitido por {offer.issuer}</span>
        </div>
      </header>

      {/* Os números do título */}
      <Card>
        <CardContent>
          <div
            className={cn(
              "grid gap-4 sm:grid-cols-2 lg:gap-0",
              metrics.length === 5 ? "lg:grid-cols-5" : metrics.length === 4 ? "lg:grid-cols-4" : "lg:grid-cols-3",
            )}
          >
            {metrics.map((m) => (
              <div key={m.label} className="grid gap-0.5 lg:border-l lg:pl-5 lg:first:border-l-0 lg:first:pl-0">
                <span className="text-xs font-medium text-muted-foreground">{m.label}</span>
                <span className={cn("font-mono text-lg font-semibold", m.tone === "success" && "text-success")}>
                  {m.value}
                </span>
                {m.detail && <span className="text-xs text-muted-foreground">{m.detail}</span>}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        {error && (
          <ErrorState
            title="Não deu para conferir o investimento"
            description="Atualize a cotação antes de investir."
            error={error}
            onRetry={() => void refetch()}
          />
        )}
        {isLoading && <Skeleton className="h-64" />}
        <div className="grid gap-5">
          {liquid ? <LiquidityInfo offer={offer} alternatives={offers ?? []} /> : quote && <Projection quote={quote} />}
          {quote && daysToRedeem !== null && (liquid || !offer.tax_exempt) && (
            <TaxSteps
              quote={quote}
              days={liquid ? heldDays : daysToRedeem}
              liquid={liquid}
              firstApplied={position?.first_applied_date ?? null}
            />
          )}
        </div>
        {quote && !error && (
          <div className="grid gap-4">
            <Card>
              <CardContent>
                <div className="grid gap-4">
                  <ToggleGroup
                    variant="segmented"
                    size="lg"
                    className="w-full *:flex-1"
                    aria-label="Investir ou resgatar"
                    value={[activeTab]}
                    onValueChange={(values) => {
                      if (values[0] === "invest" || values[0] === "redeem") setTab(values[0]);
                    }}
                  >
                    <ToggleGroupItem value="invest" tone="success" disabled={leftCatalogOn !== null}>
                      Investir
                    </ToggleGroupItem>
                    <ToggleGroupItem value="redeem" tone="dark">
                      Resgatar
                    </ToggleGroupItem>
                  </ToggleGroup>

                  {activeTab === "invest" ? (
                    <InvestmentTicket
                      assetId={id}
                      offer={offer}
                      amountText={amountText}
                      onAmountChange={setAmountText}
                      quote={quote}
                    />
                  ) : (
                    <RedemptionTicket
                      assetId={id}
                      offer={offer}
                      position={position}
                      today={today}
                      leftCatalogOn={leftCatalogOn}
                      permanentCdbId={permanentCdbId}
                      onInvest={() => setTab("invest")}
                    />
                  )}
                </div>
              </CardContent>
            </Card>
            {position && <PositionCard assetId={id} offer={offer} position={position} today={today} />}
          </div>
        )}
      </div>
    </>
  );
}

/** O dia seguinte à última data da oferta, em ISO: quando ela deixa o catálogo. */
function displayIsoNextDay(iso: string) {
  return addDays(parseLocalDate(iso), 1).toLocaleDateString("sv-SE");
}

/** Sua posição neste título: o que foi aplicado, o que rende e o que sai se resgatar tudo hoje. */
function PositionCard({
  assetId,
  offer,
  position,
  today,
}: {
  assetId: string;
  offer: FixedIncomeOffer;
  position: FixedIncomePosition;
  today: string;
}) {
  const liquid = offer.daily_liquidity;
  const { data: redemption } = useFixedIncomeRedemption(assetId, "0", today, liquid);
  const gain = Number(position.return_value);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-2.5">
          <span className="text-xs font-medium text-muted-foreground">Sua posição</span>
          <div className="grid grid-cols-2 gap-3">
            <PositionFigure
              label="Aplicado"
              detail={`desde ${displayDate(parseLocalDate(position.first_applied_date))}`}
            >
              {displayMoney(position.total_applied)}
            </PositionFigure>
            <PositionFigure label="Valor hoje" detail="bruto, antes do IR">
              {displayMoney(position.current_value)}
            </PositionFigure>
            <PositionFigure label="Rendimento" detail={displaySignedPercent(position.return_pct)} positive={gain >= 0}>
              {gain >= 0 ? "+" : ""}
              {displaySignedMoney(gain)}
            </PositionFigure>
            {liquid ? (
              <PositionFigure
                label="Se resgatar tudo hoje"
                detail={
                  redemption && Number(redemption.iof_rate) > 0
                    ? "IOF e IR sobre o rendimento"
                    : `IR de ${displayPercent(redemption?.income_tax_rate ?? 0, 1)} sobre o rendimento`
                }
              >
                {redemption ? displayMoney(redemption.max_amount) : "—"}
              </PositionFigure>
            ) : (
              <PositionFigure label="Vence em" detail={timeToMaturity(offer.maturity_date, today)}>
                {displayDate(parseLocalDate(offer.maturity_date))}
              </PositionFigure>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function PositionFigure({
  label,
  detail,
  positive,
  children,
}: {
  label: string;
  detail: string;
  positive?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-0.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className={cn("font-mono font-semibold", positive && "text-success")}>{children}</span>
      <span className="text-[11px] text-muted-foreground">{detail}</span>
    </div>
  );
}

/** O que a liquidez diária significa: o que rende, quando cai no caixa e o que se paga por isso. */
function LiquidityInfo({ offer, alternatives }: { offer: FixedIncomeOffer; alternatives: FixedIncomeOffer[] }) {
  // O melhor CDB que prende o dinheiro até o vencimento, para mostrar o que a liquidez custa
  const locked = alternatives
    .filter((o) => !o.daily_liquidity && o.rate_index === "CDI")
    .reduce<FixedIncomeOffer | null>(
      (best, o) => (!best || Number(o.interest_rate) > Number(best.interest_rate) ? o : best),
      null,
    );
  const costs = locked !== null && Number(locked.interest_rate) > Number(offer.interest_rate);

  const rate = displayRateLabel(offer.rate_index, offer.interest_rate);
  const blocks = [
    { label: "Rende até o resgate", value: rate, detail: "todo dia útil, como no vencimento" },
    { label: "Quando cai no caixa", value: "no mesmo pregão", detail: "sem esperar o vencimento" },
    costs
      ? {
          label: "O custo",
          value: "rende menos",
          detail: `o ${locked.name}, que trava até ${parseLocalDate(locked.maturity_date).getFullYear()}, paga ${displayRateLabel(locked.rate_index, locked.interest_rate)}. Liquidez diária acima de 100% só em oferta rara, com teto`,
        }
      : {
          label: "O custo",
          value: isRareOffer(offer) ? "teto e prazo" : "rende menos",
          detail: isRareOffer(offer)
            ? "oferta rara: tem teto por jogador e sai do catálogo no fim do mês"
            : "títulos que travam o dinheiro até o vencimento costumam pagar mais",
        },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resgata em qualquer dia</CardTitle>
        <CardDescription>
          Este título tem liquidez diária: o dinheiro volta ao caixa no mesmo pregão em que você pede, pelo valor
          corrigido até hoje. Serve de reserva de emergência que rende.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2.5 sm:grid-cols-3">
          {blocks.map((b) => (
            <div key={b.label} className="grid content-start gap-0.5 rounded-lg bg-background p-3">
              <span className="text-xs font-medium text-muted-foreground">{b.label}</span>
              <b className="font-mono font-semibold">{b.value}</b>
              <span className="text-xs text-muted-foreground">{b.detail}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
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

/**
 * A tabela regressiva em degraus, com a faixa do prazo em destaque. Em título de liquidez diária o prazo é
 * o tempo que o dinheiro já está aplicado (`firstApplied` é o dia da primeira aplicação, quando existe).
 */
function TaxSteps({
  quote,
  days,
  liquid,
  firstApplied,
}: {
  quote: FixedIncomeQuote;
  days: number;
  liquid: boolean;
  firstApplied: string | null;
}) {
  const brackets = quote.income_tax_brackets;
  const current = brackets.findIndex((b) => b.max_days === null || days <= b.max_days);

  return (
    <Card>
      <CardHeader>
        <CardTitle>IR cai com o tempo</CardTitle>
        <CardDescription>
          {liquid
            ? "O IR do resgate depende de há quanto tempo o dinheiro está aplicado. Quanto mais tempo, menor a alíquota sobre o rendimento."
            : "Quanto mais tempo o dinheiro fica, menor a alíquota sobre o rendimento."}
        </CardDescription>
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
                {active && (
                  <span className="text-xs text-sidebar-foreground">
                    {!liquid
                      ? `você resgata em ${days} dias`
                      : firstApplied
                        ? `seu dinheiro está há ${days} dias`
                        : "o prazo conta da primeira aplicação"}
                  </span>
                )}
                {firstApplied && i === current + 1 && (
                  <span className="text-xs text-muted-foreground">
                    a partir de {displayDate(addDays(parseLocalDate(firstApplied), from))}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
