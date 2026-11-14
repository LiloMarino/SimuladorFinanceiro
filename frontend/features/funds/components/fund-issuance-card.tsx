import { Megaphone } from "lucide-react";
import { useDeferredValue, useState } from "react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Progress } from "@/shared/components/ui/progress";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayIsoDate, displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import type { FundDetails } from "@/types";
import { useSubscribeFundIssuance } from "../hooks/mutations/useSubscribeFundIssuance";
import { useFundSubscriptionPreview } from "../hooks/queries/useFundSubscriptionPreview";
import { PREFERENCE_RIGHT } from "../lib/fund-metrics";

type Issuance = NonNullable<FundDetails["issuance"]>;

type SubscribeFormProps = { fundId: number; issuance: Issuance; rightsLeft: number };

/** Compra do direito de preferência: a quantidade vai até o que resta do direito, e a prévia diz o custo e a parte depois. */
function SubscribeForm({ fundId, issuance, rightsLeft }: SubscribeFormProps) {
  const [quotasText, setQuotasText] = useState("");
  const quotas = Number(quotasText);
  const deferredQuotas = useDeferredValue(quotas);
  const { data: preview } = useFundSubscriptionPreview(fundId, deferredQuotas);
  const subscribe = useSubscribeFundIssuance(fundId);

  const valid = Number.isInteger(quotas) && quotas > 0;
  const overRights = valid && quotas > rightsLeft;
  const noCash = valid && preview !== undefined && !preview.cash_enough;
  const ready =
    valid && preview !== undefined && deferredQuotas === quotas && !overRights && !noCash && !subscribe.isPending;

  const submit = () => {
    if (ready) subscribe.mutate({ quotas }, { onSuccess: () => setQuotasText("") });
  };

  return (
    <div className="grid gap-3 rounded-lg bg-card p-3">
      <Field data-invalid={overRights || noCash}>
        <FieldLabel htmlFor="issuance-subscribe">Quantas cotas comprar</FieldLabel>
        <div className="flex gap-2">
          <Input
            id="issuance-subscribe"
            numeric
            inputMode="numeric"
            autoComplete="off"
            placeholder={`Até ${displayQuantity(String(rightsLeft))}`}
            value={quotasText}
            aria-invalid={overRights || noCash}
            onChange={(event) => setQuotasText(formatPositiveInteger(event.target.value))}
            onKeyDown={(event) => event.key === "Enter" && submit()}
          />
          <Button variant="fund" disabled={!ready} onClick={submit}>
            {subscribe.isPending && <Spinner />}
            Comprar
          </Button>
        </div>
        {overRights ? (
          <FieldError>Seu direito restante é de {displayQuantity(String(rightsLeft))} cotas.</FieldError>
        ) : noCash ? (
          <FieldError>Seu caixa não cobre {displayMoney(preview.cost)}.</FieldError>
        ) : (
          <FieldDescription>Ao preço fixo de {displayMoney(issuance.price)} por cota.</FieldDescription>
        )}
      </Field>
      {valid && preview && !overRights && (
        <div>
          <KeyValueRow label="Custo" value={displayMoney(preview.cost)} />
          <KeyValueRow
            label="Você teria"
            value={`${displayQuantity(preview.my_quotas_after)} cotas · ${displayPercent(preview.my_share_after, 1)}`}
          />
        </div>
      )}
    </div>
  );
}

type FundIssuanceCardProps = { fund: FundDetails; viewer: boolean };

/** Cartão da emissão no topo da página: preferência dos cotistas, sobra aberta ou encerrada, com o que já nasceu. */
export function FundIssuanceCard({ fund, viewer }: FundIssuanceCardProps) {
  const issuance = fund.issuance;
  if (issuance === null) return null;

  const closed = issuance.closed_on !== null;
  const preference = issuance.phase === "preference";
  const quotas = Number(issuance.quotas);
  const sold = Number(issuance.sold);
  const rights = issuance.my_rights === null ? null : Number(issuance.my_rights);
  const rightsLeft = rights === null ? 0 : Math.max(rights - Number(issuance.my_bought ?? 0), 0);

  return (
    <Card variant={closed ? "default" : "info"}>
      <CardContent>
        <div className="grid gap-3">
          <div className="flex flex-wrap items-center gap-2.5">
            <Megaphone className="size-4 text-primary" />
            <b className="text-[15px] font-semibold">
              {closed ? "Emissão de cotas encerrada" : "Emissão de cotas em andamento"}
            </b>
            <Badge variant={closed ? "secondary" : "success"} size="tag">
              {closed
                ? `em ${displayIsoDate(issuance.closed_on ?? issuance.ends_on)}`
                : preference
                  ? "preferência dos cotistas"
                  : "sobra aberta a todos"}
            </Badge>
          </div>
          <Progress value={quotas > 0 ? (sold / quotas) * 100 : 0} aria-label="Cotas vendidas na emissão" />
          <p className="text-[13px] text-muted-foreground">
            <b className="font-mono font-semibold text-foreground">{displayQuantity(issuance.sold)}</b> de{" "}
            {displayQuantity(issuance.quotas)} cotas vendidas a {displayMoney(issuance.price)} cada, somando{" "}
            {displayMoney(issuance.raised)}
            {!closed &&
              (preference ? (
                <>
                  . A preferência vai até {displayIsoDate(issuance.preference_ends_on)} e a sobra, até{" "}
                  {displayIsoDate(issuance.ends_on)}.
                </>
              ) : (
                <>. A sobra vai até {displayIsoDate(issuance.ends_on)}.</>
              ))}
          </p>
          {!closed && viewer && preference && rights !== null && rightsLeft > 0 && (
            <>
              <p className="text-[13px]">
                <MetricLabel metric={PREFERENCE_RIGHT} />:{" "}
                <b className="font-mono font-semibold">{displayQuantity(String(rightsLeft))}</b> cotas
              </p>
              <SubscribeForm fundId={fund.id} issuance={issuance} rightsLeft={rightsLeft} />
            </>
          )}
          {!closed && viewer && preference && (rights === null || rightsLeft === 0) && (
            <p className="text-[13px] text-muted-foreground">
              {rights === null
                ? `Só quem tinha cotas no anúncio compra agora. Para você, a emissão abre em ${displayIsoDate(issuance.preference_ends_on)}.`
                : "Você já usou todo o seu direito de preferência. A sobra abre a todos depois da preferência."}
            </p>
          )}
          {!closed && viewer && !preference && (
            <p className="text-[13px] text-muted-foreground">
              A sobra está aberta: compre pelo livro de ofertas, ao preço fixo de {displayMoney(issuance.price)}.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
