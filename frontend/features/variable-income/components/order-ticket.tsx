import { useState } from "react";
import { keepPreviousData, useQueryClient } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { normalizeNumberString } from "@/shared/lib/utils";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import { displayDate, displayMoney, parseLocalDate } from "@/shared/lib/utils/display";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { OrderPreview } from "@/types";

type Action = "buy" | "sell";
type OrderKind = "market" | "limit";

const SHORTCUTS = [
  { label: "25%", share: 0.25 },
  { label: "50%", share: 0.5 },
  { label: "Máx", share: 1 },
];

/** Boleta: escolhe a ordem e mostra, antes de enviar, o que ela faz com o caixa e o IR. */
export function OrderTicket({ ticker }: { ticker: string }) {
  const queryClient = useQueryClient();
  const [action, setAction] = useState<Action>("buy");
  const [kind, setKind] = useState<OrderKind>("market");
  const [quantityText, setQuantityText] = useState("");
  const [limitText, setLimitText] = useState("");

  const quantity = Number(quantityText) || 0;
  const limitPrice = kind === "limit" ? Number(normalizeNumberString(limitText)) || null : null;
  const [request] = useDebounce({ action, quantity, limit_price: limitPrice }, 250);

  const { data: preview } = useApiQuery({
    queryKey: queryKeys.orderPreview(ticker, request),
    queryFn: ({ signal }) =>
      apiFetch<OrderPreview>(`/api/variable-income/${ticker}/order-preview`, { method: "POST", body: request, signal }),
    placeholderData: keepPreviousData,
  });

  const submit = useApiMutation({
    mutationFn: () =>
      apiFetch(`/api/variable-income/${ticker}/orders`, {
        method: "POST",
        body: { action, type: kind, quantity, limit_price: limitPrice },
      }),
    onSuccess: () => {
      setQuantityText("");
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolioPosition(ticker) });
    },
    onError: (err) => toastApiError(err),
  });

  const selling = action === "sell";
  const maxQuantity = preview?.max_quantity ?? 0;
  const overMax = quantity > maxQuantity;
  const noPosition = selling && preview !== undefined && preview.held === 0;
  const canSubmit = quantity > 0 && !overMax && !!preview?.price && (kind === "market" || !!limitPrice);

  const quantityHint = selling
    ? preview && preview.reserved > 0
      ? `Máx = ${maxQuantity}: ${preview.reserved} das suas ${preview.held} já estão em ordens abertas.`
      : `Máx = ${maxQuantity}, tudo o que você tem.`
    : `Máx = ${maxQuantity} com o caixa de hoje.`;
  const quantityError = selling
    ? `Você tem ${maxQuantity} disponíveis${preview && preview.reserved > 0 ? ` (${preview.reserved} já estão em ordens abertas)` : ""}.`
    : `O caixa paga até ${maxQuantity}.`;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nova ordem</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <ToggleGroup
            variant="segmented"
            aria-label="Comprar ou vender"
            value={[action]}
            onValueChange={(values) => values[0] && setAction(values[0] as Action)}
            className="w-full *:flex-1"
          >
            <ToggleGroupItem value="buy">Comprar</ToggleGroupItem>
            <ToggleGroupItem value="sell">Vender</ToggleGroupItem>
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
              >
                <ToggleGroupItem value="market">A mercado</ToggleGroupItem>
                <ToggleGroupItem value="limit">Limitada</ToggleGroupItem>
              </ToggleGroup>

              {/* Quantidade */}
              <Field data-invalid={overMax}>
                <FieldLabel htmlFor="order-quantity">Quantidade</FieldLabel>
                <div className="flex gap-1.5">
                  <Input
                    id="order-quantity"
                    numeric
                    inputMode="numeric"
                    value={quantityText}
                    aria-invalid={overMax}
                    onChange={(e) => setQuantityText(formatPositiveInteger(e.target.value))}
                  />
                  {SHORTCUTS.map((s) => (
                    <Button
                      key={s.label}
                      variant="outline"
                      onClick={() => setQuantityText(String(Math.floor(maxQuantity * s.share)))}
                    >
                      {s.label}
                    </Button>
                  ))}
                </div>
                {overMax ? (
                  <FieldError>{quantityError}</FieldError>
                ) : (
                  <FieldDescription>{quantityHint}</FieldDescription>
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
                    Só executa se alguém {selling ? "comprar" : "vender"} a esse preço ou {selling ? "mais" : "menos"}.
                  </FieldDescription>
                </Field>
              )}

              {/* Resumo */}
              {preview && (
                <dl className="grid gap-1.5 border-t border-muted pt-3 text-[13px]">
                  <Row
                    label={
                      kind === "limit"
                        ? "Preço limite"
                        : `Preço estimado · melhor ${selling ? "compra" : "venda"} no book`
                    }
                    value={preview.price ? displayMoney(preview.price) : "—"}
                  />
                  <Row
                    label={selling ? "Total se executar" : "Total estimado"}
                    value={displayMoney(preview.total)}
                    strong
                  />
                  <Row label="Caixa agora" value={displayMoney(preview.cash_before)} />
                  <Row label="Caixa depois" value={displayMoney(preview.cash_after)} />
                  {preview.profit !== null && (
                    <Row label="Lucro estimado · sobre o preço médio" value={displayMoney(preview.profit)} />
                  )}
                </dl>
              )}

              {selling && preview?.tax !== null && preview?.tax !== undefined && quantity > 0 && (
                <TaxEstimate preview={preview} />
              )}

              <Button
                size="lg"
                variant={selling ? "destructive" : "success"}
                disabled={!canSubmit || submit.isPending}
                onClick={() => submit.mutate()}
              >
                {submit.isPending && <Spinner />}
                {selling ? "Vender" : "Comprar"} {quantity || ""} {ticker}
                {preview?.price && quantity > 0
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

function Row({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={strong ? "font-mono font-semibold" : "font-mono"}>{value}</dd>
    </div>
  );
}

/** IR que a venda acrescenta ao mês, com a régua da isenção de ações. */
function TaxEstimate({ preview }: { preview: OrderPreview }) {
  const sales = Number(preview.month_stock_sales_after ?? 0);
  const limit = Number(preview.stock_sales_exemption);
  const scale = Math.max(sales, limit) * 1.25;
  const taxed = Number(preview.tax) > 0;
  const due = preview.tax_due_date ? displayDate(parseLocalDate(preview.tax_due_date)) : null;

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
            sales > limit
              ? "absolute inset-y-0 left-0 rounded-full bg-warning"
              : "absolute inset-y-0 left-0 rounded-full bg-primary"
          }
          style={{ width: `${(sales / scale) * 100}%` }}
        />
        <span className="absolute -top-1 h-3.5 w-0.5 bg-foreground" style={{ left: `${(limit / scale) * 100}%` }} />
      </div>
      <p className="text-muted-foreground">
        {sales > limit
          ? `Com esta venda, as vendas de ações do mês vão a ${displayMoney(sales)}, acima dos ${displayMoney(limit)} isentos. O lucro paga imposto${due ? `, cobrado em ${due}` : ""}.`
          : taxed
            ? `O lucro paga imposto mesmo dentro dos ${displayMoney(limit)}: FII, ETF, BDR e day trade não têm isenção${due ? `. Cobrado em ${due}` : ""}.`
            : `As vendas de ações do mês ficam em ${displayMoney(sales)}, dentro dos ${displayMoney(limit)} isentos: o lucro não paga IR.`}
      </p>
    </div>
  );
}
