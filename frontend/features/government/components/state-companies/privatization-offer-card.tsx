import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Progress } from "@/shared/components/ui/progress";
import { displayMoney, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { StateOffer } from "@/types";
import { useReserveStateOffer } from "../../hooks/mutations/useReserveStateOffer";
import { FAIR_VALUE } from "../../lib/government-metrics";
import {
  offerDaysLabel,
  offerPremium,
  premiumLabel,
  reservationCost,
  reservedShare,
  unitPrice,
} from "../../lib/state-companies";

type PrivatizationOfferCardProps = {
  offer: StateOffer;
  /** O dia da partida agora, para a contagem dos dias que faltam */
  today: string;
};

type FactProps = { label: React.ReactNode; value: React.ReactNode; note?: React.ReactNode };

function Fact({ label, value, note }: FactProps) {
  return (
    <div className="grid content-start gap-0.5">
      <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">{label}</span>
      <span className="font-mono text-base leading-tight font-semibold tabular-nums">{value}</span>
      {note && <span className="text-xs leading-snug text-muted-foreground">{note}</span>}
    </div>
  );
}

/** A oferta de privatização aberta a todos: o preço pelo valor justo, o que a sala já pediu e a reserva de quem vê. */
export function PrivatizationOfferCard({ offer, today }: PrivatizationOfferCardProps) {
  const reserve = useReserveStateOffer();
  const [quantity, setQuantity] = useState(offer.your_reservation ? String(Number(offer.your_reservation)) : "");

  const count = Number(quantity);
  const cost = reservationCost(offer, count);
  const premium = offerPremium(offer);
  const premiumText = premium === null ? null : premiumLabel(premium);
  const overCash = cost > Number(offer.your_cash);
  const requested = reservedShare(offer);

  return (
    <Card variant="info">
      <CardContent>
        <div className="grid min-w-0 gap-4">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-[15px] font-semibold">
              Privatização da {offer.name} <span className="font-mono text-xs">{offer.ticker}</span>
            </h2>
            <Badge variant="warning">{offerDaysLabel(offer, today)}</Badge>
          </div>
          <p className="text-[13px] text-muted-foreground">
            O governo vende a fatia dele a quem reservar, e o Mercado do jogo compra o que sobrar. O preço é o valor
            justo do último dia da oferta; se a sala pedir mais ações do que há, cada um recebe a mesma proporção do que
            pediu.
          </p>

          {/* Números da oferta */}
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Fact
              label={
                <>
                  {FAIR_VALUE.label}
                  <MetricHint metric={FAIR_VALUE} />
                </>
              }
              value={unitPrice(offer.price)}
              note="Preço por ação da oferta"
            />
            <Fact label="Ações à venda" value={displayNumber(offer.shares, 0)} />
            <Fact label="Preço na bolsa" value={unitPrice(offer.market_price)} note={premiumText} />
            <Fact
              label="Já reservado"
              value={`${displayPercent(requested, 0)} das ações`}
              note={
                <span className="grid gap-1.5">
                  <Progress
                    value={Math.min(100, requested * 100)}
                    size="sm"
                    aria-label="Parte das ações à venda que a sala já reservou"
                  />
                  {requested > 1
                    ? `${displayNumber(Number(offer.reserved), 0)} pedidas para ${displayNumber(offer.shares, 0)}: o rateio é proporcional`
                    : `${displayNumber(Number(offer.reserved), 0)} de ${displayNumber(offer.shares, 0)} ações`}
                </span>
              }
            />
          </div>

          {/* Reserva */}
          <form
            className="grid gap-3 sm:grid-cols-[minmax(0,16rem)_auto] sm:items-end"
            onSubmit={(event) => {
              event.preventDefault();
              reserve.mutate({ ticker: offer.ticker, quantity: count });
            }}
          >
            <Field>
              <FieldLabel htmlFor={`reserve-${offer.ticker}`}>
                {offer.your_reservation ? "Sua reserva (ações)" : "Quantas ações reservar"}
              </FieldLabel>
              <Input
                id={`reserve-${offer.ticker}`}
                numeric
                inputMode="numeric"
                value={quantity}
                onChange={(event) => setQuantity(event.target.value.replace(/\D/g, ""))}
              />
              {overCash ? (
                <FieldError>Seu caixa hoje é {displayMoney(offer.your_cash)}.</FieldError>
              ) : (
                <FieldDescription>
                  {count > 0 ? `Custa ${displayMoney(cost)} no fechamento. ` : ""}Seu caixa:{" "}
                  {displayMoney(offer.your_cash)}
                </FieldDescription>
              )}
            </Field>
            <Button type="submit" disabled={reserve.isPending || count <= 0 || overCash}>
              {offer.your_reservation ? "Atualizar reserva" : "Reservar"}
            </Button>
          </form>

          {premium !== null && premium > 0.005 && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>A oferta custa mais que a bolsa</AlertTitle>
              <AlertDescription>
                {premiumText}: pelas mesmas ações, a bolsa cobra {unitPrice(offer.market_price)} contra{" "}
                {unitPrice(offer.price)} da oferta.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
