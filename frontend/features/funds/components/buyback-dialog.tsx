import { useDeferredValue, useState } from "react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
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
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import { useOpenFundBuyback } from "../hooks/mutations/useOpenFundBuyback";
import { useFundBuybackPreview } from "../hooks/queries/useFundBuybackPreview";
import { BUYBACK_PREMIUM_COST } from "@/shared/lib/fund-metrics";
import { ControlNotice } from "@/shared/components/control-notice";
import type { FundDetails } from "@/types";

type BuybackDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fund: FundDetails;
};

/** Recompra: a gestora compra cotas no livro, com o próprio caixa, até o preço máximo, e as cotas compradas deixam de existir. */
export function BuybackDialog({ open, onOpenChange, fund }: BuybackDialogProps) {
  const fundId = fund.id;
  const totalQuotas = Number(fund.quotas);
  const [quantityText, setQuantityText] = useState("");
  const [priceText, setPriceText] = useState("");
  const quantity = Number(quantityText);
  const maxPrice = normalizeNumberString(priceText) || "0";
  const deferredQuantity = useDeferredValue(quantity);
  const deferredPrice = useDeferredValue(maxPrice);
  const { preview } = useFundBuybackPreview(fundId, deferredQuantity, deferredPrice);
  const openBuyback = useOpenFundBuyback(fundId);

  const valid = Number.isInteger(quantity) && quantity > 0 && Number(maxPrice) > 0;
  const tooMany = quantity >= totalQuotas && quantity > 0;
  const noCash = valid && preview !== undefined && !preview.cash_enough;
  const settled = preview !== undefined && deferredQuantity === quantity && deferredPrice === maxPrice;
  const ready = valid && settled && !tooMany && !noCash;
  const premium = preview ? Number(preview.premium) : 0;
  const cashNow = Number(fund.composition.find((item) => item.asset_class === "cash")?.value ?? 0);

  const submit = () => {
    if (ready && !openBuyback.isPending) {
      openBuyback.mutate({ quantity, max_price: maxPrice }, { onSuccess: () => onOpenChange(false) });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-145">
        <DialogHeader variant="divided">
          <DialogTitle>Recompra de cotas</DialogTitle>
          <DialogDescription>
            A gestora compra {fund.ticker} no livro com o caixa dela, e as cotas compradas deixam de existir.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field data-invalid={tooMany}>
              <FieldLabel htmlFor="buyback-quantity">Quantas cotas</FieldLabel>
              <Input
                id="buyback-quantity"
                autoFocus
                numeric
                inputMode="numeric"
                autoComplete="off"
                placeholder="Ex.: 500"
                value={quantityText}
                aria-invalid={tooMany}
                onChange={(event) => setQuantityText(formatPositiveInteger(event.target.value))}
              />
              {tooMany ? (
                <FieldError>Recomprar tudo acaba com a gestora: deixe ao menos uma cota.</FieldError>
              ) : (
                <FieldDescription>Existem {displayQuantity(String(totalQuotas))} cotas hoje.</FieldDescription>
              )}
            </Field>
            <Field>
              <FieldLabel htmlFor="buyback-price">Preço máximo por cota</FieldLabel>
              <Input
                id="buyback-price"
                numeric
                inputMode="decimal"
                autoComplete="off"
                placeholder="R$ 0,00"
                value={priceText}
                onChange={(event) => setPriceText(formatMoney(event.target.value))}
                onKeyDown={(event) => event.key === "Enter" && submit()}
              />
              <FieldDescription>
                Hoje o livro vende a {fund.price === null ? "—" : displayMoney(fund.price)}. A ordem não paga mais que
                isso por cota.
              </FieldDescription>
            </Field>
          </div>
          {valid && preview && !tooMany && (
            <>
              <div>
                <KeyValueRow
                  label="Custa até"
                  value={displayMoney(preview.cost)}
                  note={`Do caixa da gestora, de ${displayMoney(cashNow)}`}
                />
                {premium > 0 && (
                  <KeyValueRow
                    label={<MetricLabel metric={BUYBACK_PREMIUM_COST} />}
                    value={displayMoney(preview.premium_cost)}
                  />
                )}
                <KeyValueRow label="Caixa da gestora depois" value={displayMoney(preview.cash_after)} />
                <KeyValueRow
                  label="Patrimônio por cota"
                  value={`${displayMoney(preview.nav)} → ${displayMoney(preview.nav_after)}`}
                  valueClassName={premium > 0 ? "text-destructive" : "text-success"}
                  note={`${premium > 0 ? "Ágio" : "Deságio"} de ${displayPercent(Math.abs(premium), 1)} sobre o patrimônio`}
                />
                <KeyValueRow
                  label="Seu controle"
                  value={`${displayPercent(preview.share_now, 1)} → ${displayPercent(preview.share_after, 1)}`}
                  note={`De ${displayQuantity(preview.total_after)} cotas`}
                />
              </div>
              {noCash && (
                <Alert variant="destructive">
                  <AlertTitle>A gestora não tem caixa para isso</AlertTitle>
                  <AlertDescription>
                    Faltam {displayMoney(-Number(preview.cash_after))} no caixa para pagar tudo ao preço máximo.
                  </AlertDescription>
                </Alert>
              )}
              <ControlNotice
                keepsControl={preview.keeps_control_after}
                title={preview.keeps_control_after ? "Você mantém o controle" : "Você perde o controle"}
              >
                Sem as cotas recompradas, a sua parte vai de {displayPercent(preview.share_now, 1)} para{" "}
                {displayPercent(preview.share_after, 1)} das {displayQuantity(preview.total_after)} cotas.
              </ControlNotice>
            </>
          )}
        </DialogBody>
        <DialogFooter variant="divided">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button variant="fund" disabled={!ready || openBuyback.isPending} onClick={submit}>
            {openBuyback.isPending && <Spinner />}
            Recomprar{valid ? ` até ${displayQuantity(String(quantity))} cotas` : ""}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
