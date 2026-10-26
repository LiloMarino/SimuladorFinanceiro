import { useState } from "react";
import { useDebounce } from "use-debounce";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Spinner } from "@/shared/components/ui/spinner";
import { useTradeLock } from "@/shared/hooks/useTradeLock";
import { TradeLockNotice } from "@/shared/components/trade-lock-notice";
import { ErrorState } from "@/shared/components/error-state";
import { cn } from "@/shared/lib/utils";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatMoney, formatQuantityInput, quantityToInput } from "@/shared/lib/utils/format";
import { displayDate, displayMoney, displayQuantity, parseLocalDate, toCentsString } from "@/shared/lib/utils/display";
import { EXEMPT_SALES_LABEL, INCOME_TAX_RATE, salesMonthName } from "@/shared/lib/income-tax";
import { displayPercent } from "@/shared/lib/utils/display";
import type { AssetClass, OrderPreview, OrderPreviewRequest } from "@/types";
import { useOrderPreview } from "../hooks/queries/useOrderPreview";
import { useSubmitOrder } from "../hooks/mutations/useSubmitOrder";

type Action = "buy" | "sell";
type OrderKind = "market" | "limit";
type SizeMode = "quantity" | "amount";

const SHORTCUTS = [
  { label: "25%", share: 0.25 },
  { label: "50%", share: 0.5 },
  { label: "Máx", share: 1 },
];

type OrderTicketProps = {
  ticker: string;
  assetClass: AssetClass;
  /** Último fechamento: a referência de hoje sob o preço limite */
  todayPrice: number;
};

/** Boleta: escolhe a ordem e mostra, antes de enviar, o que ela faz com o caixa e o IR. */
export function OrderTicket({ ticker, assetClass, todayPrice }: OrderTicketProps) {
  const [action, setAction] = useState<Action>("buy");
  const [kind, setKind] = useState<OrderKind>("market");
  const [mode, setMode] = useState<SizeMode>("quantity");
  const [quantityText, setQuantityText] = useState("");
  const [amountText, setAmountText] = useState("");
  const [limitText, setLimitText] = useState("");

  // Só a cripto aceita fração; a API recebe a quantidade como string decimal
  const fractional = assetClass === "CRYPTO";
  const quantity = quantityText.replace(",", ".").replace(/\.$/, "") || "0";
  const quantityNumber = Number(quantity);
  const amount = normalizeNumberString(amountText) || "0";
  const amountNumber = Number(amount);
  const limitPrice = kind === "limit" ? Number(normalizeNumberString(limitText)) || null : null;

  // O valor em reais só existe na compra a mercado; venda e Limitada medem a ordem em quantidade
  const buyingAtMarket = action === "buy" && kind === "market";
  const byAmount = buyingAtMarket && mode === "amount";
  const size: Pick<OrderPreviewRequest, "quantity" | "amount"> = byAmount ? { amount } : { quantity };
  const [request] = useDebounce({ action, ...size, limit_price: limitPrice }, 250);

  const { data: preview, error, isLoading, refetch } = useOrderPreview(ticker, request);
  const requestMatches =
    request.action === action &&
    request.quantity === size.quantity &&
    request.amount === size.amount &&
    request.limit_price === limitPrice;

  const submit = useSubmitOrder(ticker);
  // Com o automático ligado a boleta fica só para leitura
  const tradeLock = useTradeLock();
  const locked = tradeLock !== null;

  const selling = action === "sell";
  const maxQuantity = preview?.max_quantity ?? "0";
  const cash = Number(preview?.cash_before ?? 0);
  const overMax = !byAmount && quantityNumber > Number(maxQuantity);
  const overCash = byAmount && preview !== undefined && amountNumber > cash;
  // Por valor, o preço estimado não paga nem uma unidade
  const belowUnit =
    byAmount &&
    requestMatches &&
    preview?.price != null &&
    amountNumber > 0 &&
    !overCash &&
    Number(preview.quantity) === 0;
  const invalidSize = overMax || overCash || belowUnit;
  const noPosition = selling && requestMatches && preview !== undefined && Number(preview.held) === 0;
  const hasSize = byAmount ? amountNumber > 0 : quantityNumber > 0;
  const canSubmit =
    !locked &&
    requestMatches &&
    !error &&
    hasSize &&
    !invalidSize &&
    !!preview?.price &&
    (kind === "market" || !!limitPrice);

  const quantityHint = selling
    ? preview && Number(preview.reserved) > 0
      ? `Máx = ${displayQuantity(maxQuantity)}: ${displayQuantity(preview.reserved)} das suas ${displayQuantity(preview.held)} já estão em ordens abertas.`
      : `Máx = ${displayQuantity(maxQuantity)}, tudo o que você tem.`
    : buyingAtMarket
      ? `O caixa paga até ${displayQuantity(maxQuantity)}. Se o preço subir antes da execução, compra até onde o caixa pagar.`
      : `Máx = ${displayQuantity(maxQuantity)} com o caixa de hoje.`;
  const amountHint =
    amountNumber === 0 || error
      ? null
      : requestMatches && preview
        ? `≈ ${displayQuantity(preview.quantity)} ${ticker} (estimado) ao melhor preço de venda, ${displayMoney(preview.price ?? 0)}.`
        : `≈ … ${ticker} (estimado)`;
  const quantityError = selling
    ? `Você tem ${displayQuantity(maxQuantity)} disponíveis${preview && Number(preview.reserved) > 0 ? ` (${displayQuantity(preview.reserved)} já estão em ordens abertas)` : ""}.`
    : `O caixa paga até ${displayQuantity(maxQuantity)}.`;
  const minimumUnit = fractional ? "0,00000001" : "1";
  const amountError = overCash
    ? `O caixa tem ${displayMoney(cash)}.`
    : `${displayMoney(amountNumber)} não paga ${minimumUnit} ${ticker} (${displayMoney(preview?.price ?? 0)}).`;

  // Tudo gasta o caixa inteiro, em reais; as frações valem na unidade do modo ativo
  const fillShortcut = (share: number) => {
    if (!preview) return;
    if (buyingAtMarket && share === 1) {
      setMode("amount");
      setAmountText(formatMoney(toCentsString(preview.cash_before)));
    } else if (byAmount) {
      setAmountText(formatMoney(toCentsString(String(cash * share))));
    } else {
      setQuantityText(quantityToInput(share === 1 ? maxQuantity : Number(maxQuantity) * share, fractional));
    }
  };

  const sendOrder = () =>
    submit.mutate(
      byAmount ? { action, type: kind, amount } : { action, type: kind, quantity, limit_price: limitPrice },
      {
        onSuccess: () => {
          setQuantityText("");
          setAmountText("");
        },
      },
    );

  // Na compra por valor a quantidade é estimada: o resumo marca com ≈ enquanto houver o que estimar
  const approx = preview && Number(preview.quantity) > 0 ? "≈ " : "";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nova ordem</CardTitle>
      </CardHeader>
      <CardContent>
        {tradeLock && <TradeLockNotice lock={tradeLock} />}
        <div inert={locked} className={cn("grid gap-4", locked && "mt-4 opacity-55")}>
          <ToggleGroup
            variant="segmented"
            size="lg"
            aria-label="Comprar ou vender"
            value={[action]}
            onValueChange={(values) => values[0] && setAction(values[0] as Action)}
            className="w-full *:flex-1"
          >
            <ToggleGroupItem value="buy" tone="success">
              Comprar
            </ToggleGroupItem>
            <ToggleGroupItem value="sell" tone="destructive">
              Vender
            </ToggleGroupItem>
          </ToggleGroup>

          {noPosition ? (
            <Empty variant="dashed">
              <EmptyHeader>
                <EmptyTitle>Você não tem {ticker}</EmptyTitle>
                <EmptyDescription>
                  Pra vender, primeiro compre. Venda a descoberto não existe no simulador.
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <>
              <ToggleGroup
                variant="segmented"
                aria-label="Tipo de ordem"
                value={[kind]}
                onValueChange={(values) => values[0] && setKind(values[0] as OrderKind)}
                className="w-full *:flex-1"
              >
                <ToggleGroupItem value="market">A mercado</ToggleGroupItem>
                <ToggleGroupItem value="limit">Limitada</ToggleGroupItem>
              </ToggleGroup>

              {/* Quantidade ou valor */}
              <Field data-invalid={invalidSize}>
                <div className="flex min-h-6.5 items-center justify-between">
                  <FieldLabel htmlFor="order-size">{byAmount ? "Valor" : "Quantidade"}</FieldLabel>
                  {buyingAtMarket && (
                    <ToggleGroup
                      variant="segmented"
                      size="xs"
                      aria-label="Medir a ordem por"
                      value={[mode]}
                      onValueChange={(values) => values[0] && setMode(values[0] as SizeMode)}
                    >
                      <ToggleGroupItem value="quantity">Quantidade</ToggleGroupItem>
                      <ToggleGroupItem value="amount">Valor</ToggleGroupItem>
                    </ToggleGroup>
                  )}
                </div>
                <div className="flex gap-1.5">
                  <Input
                    id="order-size"
                    numeric
                    inputMode={byAmount || !fractional ? "numeric" : "decimal"}
                    value={byAmount ? amountText : quantityText}
                    aria-invalid={invalidSize}
                    onChange={(e) =>
                      byAmount
                        ? setAmountText(formatMoney(e.target.value))
                        : setQuantityText(formatQuantityInput(e.target.value, fractional))
                    }
                  />
                  {SHORTCUTS.map((s) => (
                    <Button key={s.label} variant="outline" onClick={() => fillShortcut(s.share)}>
                      {buyingAtMarket && s.share === 1 ? "Tudo" : s.label}
                    </Button>
                  ))}
                </div>
                {invalidSize ? (
                  <FieldError>{byAmount ? amountError : quantityError}</FieldError>
                ) : (
                  <FieldDescription>{byAmount ? amountHint : quantityHint}</FieldDescription>
                )}
              </Field>

              {kind === "limit" && (
                <Field>
                  <FieldLabel htmlFor="order-limit">Preço limite</FieldLabel>
                  <Input
                    id="order-limit"
                    numeric
                    inputMode="decimal"
                    value={limitText}
                    onChange={(e) => setLimitText(e.target.value)}
                    placeholder="0,00"
                  />
                  <FieldDescription>
                    Só executa se alguém {selling ? "comprar" : "vender"} a{" "}
                    <b className="font-mono text-foreground">{limitPrice ? displayMoney(limitPrice) : "esse preço"}</b>{" "}
                    ou {selling ? "mais" : "menos"}. Hoje:{" "}
                    <b className="font-mono text-foreground">{displayMoney(todayPrice)}</b>.
                  </FieldDescription>
                </Field>
              )}

              {error && (
                <ErrorState
                  title="Não deu para conferir a ordem"
                  description="Atualize a prévia antes de enviar."
                  error={error}
                  onRetry={() => void refetch()}
                />
              )}
              {(isLoading || !requestMatches) && (
                <p role="status" className="text-sm text-muted-foreground">
                  Conferindo a ordem…
                </p>
              )}

              {/* Resumo: a venda mostra só o total e o lucro */}
              {preview ? (
                <dl className="grid gap-1.5 border-t border-muted pt-3 text-[13px]">
                  {selling ? (
                    <>
                      <Row label="Total se executar" value={displayMoney(preview.total)} strong />
                      {preview.profit !== null && (
                        <Row
                          label={`Lucro estimado · sobre preço médio ${displayMoney(averagePrice(preview, quantityNumber))}`}
                          value={`${Number(preview.profit) >= 0 ? "+" : "-"}${displayMoney(Math.abs(Number(preview.profit)))}`}
                          tone={Number(preview.profit) >= 0 ? "positive" : "negative"}
                        />
                      )}
                    </>
                  ) : (
                    <>
                      <Row
                        label={kind === "limit" ? "Preço limite" : "Preço estimado · melhor venda no book"}
                        value={preview.price ? displayMoney(preview.price) : "—"}
                      />
                      {byAmount && (
                        <Row
                          label="Quantidade estimada"
                          value={overCash ? "—" : `${approx}${displayQuantity(preview.quantity)}`}
                        />
                      )}
                      <Row
                        label="Total estimado"
                        value={overCash ? "—" : `${byAmount ? approx : ""}${displayMoney(preview.total)}`}
                        strong
                      />
                      <Row label="Caixa agora" value={displayMoney(preview.cash_before)} />
                      <Row
                        label="Caixa depois"
                        value={overCash ? "—" : `${byAmount ? approx : ""}${displayMoney(preview.cash_after)}`}
                      />
                    </>
                  )}
                </dl>
              ) : (
                !error && <SummarySkeleton rows={selling ? 2 : 4} />
              )}

              {selling && preview?.tax !== null && preview?.tax !== undefined && quantityNumber > 0 && (
                <TaxEstimate preview={preview} assetClass={assetClass} />
              )}

              <Button
                size="lg"
                variant={selling ? "destructive" : "success"}
                disabled={!canSubmit || submit.isPending}
                onClick={sendOrder}
              >
                {submit.isPending && <Spinner />}
                {selling ? "Vender" : "Comprar"}{" "}
                {byAmount ? (amountNumber > 0 ? `${amountText} em ${ticker}` : ticker) : `${quantityText} ${ticker}`}
                {!byAmount && preview?.price && quantityNumber > 0
                  ? kind === "limit"
                    ? ` a ${displayMoney(preview.price)}`
                    : ` · ${displayMoney(preview.total)}`
                  : ""}
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/** Linhas do resumo enquanto a prévia carrega. */
function SummarySkeleton({ rows }: { rows: number }) {
  return (
    <div className="grid gap-2.5 border-t border-muted pt-3">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="flex justify-between">
          <Skeleton className="h-3.5 w-[150px]" />
          <Skeleton className="h-3.5 w-20" />
        </div>
      ))}
    </div>
  );
}

/** Preço médio da posição: o preço da ordem menos o lucro por ação. */
function averagePrice(preview: OrderPreview, quantity: number) {
  return Number(preview.price) - Number(preview.profit) / quantity;
}

function Row({
  label,
  value,
  strong = false,
  tone,
}: {
  label: string;
  value: string;
  strong?: boolean;
  tone?: "positive" | "negative" | undefined;
}) {
  const color = tone === "positive" ? "text-success" : tone === "negative" ? "text-destructive" : "";
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={`font-mono ${strong ? "font-semibold" : ""} ${color}`}>{value}</dd>
    </div>
  );
}

/** IR que a venda acrescenta ao mês, com a régua da isenção da classe (ação ou cripto). */
function TaxEstimate({ preview, assetClass }: { preview: OrderPreview; assetClass: AssetClass }) {
  const sales = EXEMPT_SALES_LABEL[assetClass];
  const after = Number(preview.month_sales_after ?? 0);
  const limit = Number(preview.exemption_limit);
  // As vendas do mês só crescem com a venda de uma classe que tem isenção
  const before = sales ? after - Number(preview.total) : after;
  // A barra enche com vendas / limite; passando do limite, a marca recua para a posição real dele
  const scale = Math.max(after, limit) || 1;
  const taxed = Number(preview.tax) > 0;
  const due = preview.tax_due_date ? displayDate(parseLocalDate(preview.tax_due_date)) : null;
  const month = preview.tax_due_date ? salesMonthName(preview.tax_due_date) : null;
  const rate = displayPercent(INCOME_TAX_RATE[assetClass], 0);
  const profit = displayMoney(preview.profit ?? 0);

  return (
    <div className="grid gap-2 rounded-[10px] bg-warning-soft/60 p-3.5 text-[13px]">
      <div className="flex justify-between">
        <span className="font-semibold">IR estimado nessa venda</span>
        <span className={taxed ? "font-mono font-semibold text-destructive" : "font-mono font-semibold"}>
          {displayMoney(preview.tax ?? 0)}
        </span>
      </div>
      <div className="relative h-1.5 rounded-full bg-card">
        <span
          className={
            after > limit
              ? "absolute inset-y-0 left-0 rounded-full bg-warning"
              : "absolute inset-y-0 left-0 rounded-full bg-primary"
          }
          style={{ width: `${(after / scale) * 100}%` }}
        />
        <span className="absolute -top-1 h-3.5 w-0.5 bg-foreground" style={{ left: `${(limit / scale) * 100}%` }} />
      </div>
      <p className="text-muted-foreground">
        {sales && after > limit ? (
          <>
            Em {month} você já vendeu {displayMoney(before)} em {sales}; com esta venda vai a {displayMoney(after)},
            acima dos {displayMoney(limit)} isentos.{" "}
            {taxed ? (
              <>
                O lucro de <b className="font-mono text-foreground">{profit}</b> paga {rate}
                {due ? `, cobrado em ${due}` : ""}.
              </>
            ) : (
              "Sem lucro, não há imposto."
            )}
          </>
        ) : taxed ? (
          <>
            O lucro de <b className="font-mono text-foreground">{profit}</b> paga {rate}
            {due ? `, cobrado em ${due}` : ""}.{sales ? "" : " FII, ETF, BDR e day trade não têm isenção."}
          </>
        ) : (
          `As vendas de ${sales ?? "ações"} do mês ficam em ${displayMoney(after)}, dentro dos ${displayMoney(limit)} isentos: o lucro não paga IR.`
        )}
      </p>
    </div>
  );
}
