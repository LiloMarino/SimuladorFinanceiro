import { useState, type Ref } from "react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { TradeLockNotice } from "@/shared/components/trade-lock-notice";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Spinner } from "@/shared/components/ui/spinner";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { useTradeLock } from "@/shared/hooks/useTradeLock";
import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import type { FundDetails } from "@/types";
import { useSubmitOrder } from "@/shared/hooks/mutations/useSubmitOrder";
import {
  holdingAfterBuy,
  holdingAfterSell,
  premium,
  premiumPaid,
  quotasToControl,
  sellableKeepingControl,
} from "../lib/fund-math";
import { fundStage } from "../lib/fund-view";
import { ControlNotice } from "./control-notice";
import { useOperatingAsFund } from "../hooks/useOperatingAsFund";
import { PersonalAccountNotice } from "./personal-account-notice";

type Side = "buy" | "sell";

type FundOrderPanelProps = {
  fund: FundDetails;
  /** Quem olha a gestora de fora só compra; o gestor vende as próprias cotas */
  viewer: boolean;
  /** O campo da quantidade, para o botão "Comprar na oferta" levar o foco até ele */
  quantityRef?: Ref<HTMLInputElement>;
};

/** Comprar e vender cotas a mercado: o preço, o ágio pago e quanto da gestora o jogador passa a ter. */
export function FundOrderPanel({ fund, viewer, quantityRef }: FundOrderPanelProps) {
  const [side, setSide] = useState<Side>(viewer ? "buy" : "sell");
  const [quantityText, setQuantityText] = useState("");
  const submit = useSubmitOrder(fund.ticker);
  const tradeLock = useTradeLock();
  const operatingAsFund = useOperatingAsFund();

  const stage = fundStage(fund);
  const inOffer = stage === "offer";
  const buying = side === "buy";
  const total = Number(fund.quotas);
  const mine = Number(fund.my_quotas);
  const nav = fund.nav === null ? null : Number(fund.nav);
  // Na oferta a cota custa o patrimônio por cota; depois, o último preço do mercado
  const price = buying && inOffer ? Number(fund.offer_price ?? fund.nav ?? 0) : Number(fund.price ?? fund.nav ?? 0);
  const quantity = Number(quantityText);
  const hasQuantity = Number.isInteger(quantity) && quantity > 0;
  const qty = hasQuantity ? quantity : 0;
  const overHeld = !buying && qty > mine;

  const after = buying ? holdingAfterBuy(mine, total, qty, inOffer) : holdingAfterSell(mine, total, qty);
  const hadControl = !viewer && quotasToControl(mine, total) === 0;
  const losesControl = !buying && !viewer && hadControl && quotasToControl(after.quotas, total) > 0;
  const sellable = sellableKeepingControl(mine, total);

  const locked = tradeLock !== null;
  const canSubmit = hasQuantity && !overHeld && !locked && !submit.isPending && price > 0;

  const place = (size: number) =>
    submit.mutate({ action: side, type: "market", quantity: String(size) }, { onSuccess: () => setQuantityText("") });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{inOffer && buying ? "Comprar na oferta" : "Comprar e vender cotas"}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <Tabs value={side} onValueChange={(next) => setSide(next as Side)}>
            <TabsList className="w-full">
              <TabsTrigger value="buy">Comprar</TabsTrigger>
              <TabsTrigger value="sell" disabled={mine === 0}>
                Vender
              </TabsTrigger>
            </TabsList>
          </Tabs>

          {operatingAsFund && (
            <PersonalAccountNotice>
              As cotas entram e saem da sua carteira pessoal. Volte para ela para comprar ou vender.
            </PersonalAccountNotice>
          )}
          {tradeLock && <TradeLockNotice lock={tradeLock} />}

          <Field data-invalid={overHeld}>
            <FieldLabel htmlFor="fund-order-quantity">Quantas cotas</FieldLabel>
            <Input
              id="fund-order-quantity"
              ref={quantityRef}
              numeric
              inputMode="numeric"
              autoComplete="off"
              placeholder="Ex.: 50"
              value={quantityText}
              aria-invalid={overHeld}
              disabled={operatingAsFund || locked}
              onChange={(event) => setQuantityText(formatPositiveInteger(event.target.value))}
            />
            <FieldDescription>
              {buying
                ? "Se o preço subir antes da execução, a compra sai pelo preço novo."
                : overHeld
                  ? `Você tem ${displayQuantity(fund.my_quotas)} cotas.`
                  : `Você tem ${displayQuantity(fund.my_quotas)} cotas para vender.`}
            </FieldDescription>
          </Field>

          <div>
            <KeyValueRow
              label={buying && inOffer ? "Preço fixo da oferta" : "Preço por cota"}
              value={price > 0 ? displayMoney(price) : "—"}
            />
            {buying && nav !== null && price > 0 && (
              <KeyValueRow
                label={`Ágio pago (${displayPercent(premium(price, nav), 1)})`}
                value={displayMoney(premiumPaid(qty, price, nav))}
              />
            )}
            <KeyValueRow label="Total estimado" value={displayMoney(qty * price)} total />
            <KeyValueRow
              label={buying ? "Você passa a ter" : "Você fica com"}
              value={`${displayQuantity(String(after.quotas))} cotas · ${displayPercent(after.share, 1)}`}
            />
          </div>

          {losesControl && hasQuantity && (
            <ControlNotice keepsControl={false} title="Você perde o controle">
              Com {displayQuantity(String(after.quotas))} cotas você fica com {displayPercent(after.share, 1)}, abaixo
              dos 50%. Sem eles, outro cotista pode passar à frente de você.
            </ControlNotice>
          )}

          {losesControl ? (
            <div className="grid gap-2">
              <Button
                variant="fund"
                disabled={sellable === 0 || locked || operatingAsFund || submit.isPending}
                onClick={() => place(sellable)}
              >
                Vender só {displayQuantity(String(sellable))}
              </Button>
              <Button variant="outline-destructive" disabled={!canSubmit} onClick={() => place(qty)}>
                {submit.isPending && <Spinner />}
                Vender {displayQuantity(String(qty))} mesmo assim
              </Button>
            </div>
          ) : (
            <Button variant="fund" disabled={!canSubmit || operatingAsFund} onClick={() => place(qty)}>
              {submit.isPending && <Spinner />}
              {buying ? "Comprar" : "Vender"}
              {hasQuantity ? ` ${displayQuantity(String(qty))} cotas` : ""}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
