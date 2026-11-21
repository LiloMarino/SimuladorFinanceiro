import { Megaphone } from "lucide-react";
import { useDeferredValue, useState } from "react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { QuantityShortcuts } from "@/shared/components/quantity-shortcuts";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Progress } from "@/shared/components/ui/progress";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayIsoDate, displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import { quantityOfShare } from "@/shared/lib/quantity-shortcuts";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import type { FundDetails } from "@/types";
import { useSubscribeFundIssuance } from "../hooks/mutations/useSubscribeFundIssuance";
import { useFundSubscriptionPreview } from "../hooks/queries/useFundSubscriptionPreview";
import { PREFERENCE_RIGHT } from "@/shared/lib/fund-metrics";
import { rightsLeftOf } from "../lib/fund-pending";
import { IssuanceEstimate } from "./issuance-estimate";

type Issuance = NonNullable<FundDetails["issuance"]>;

type SubscribeFormProps = { fundId: number; issuance: Issuance; rightsLeft: number };

/** Compra do direito de preferência: a quantidade vai até o que resta do direito, e a prévia diz o custo, a parte depois e o teto que o caixa paga. */
function SubscribeForm({ fundId, issuance, rightsLeft }: SubscribeFormProps) {
  const [quotasText, setQuotasText] = useState("");
  const quotas = Number(quotasText);
  const deferredQuotas = useDeferredValue(quotas);
  const { data: preview } = useFundSubscriptionPreview(fundId, Math.max(deferredQuotas, 1));
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
        <QuantityShortcuts
          size="sm"
          className="*:flex-1"
          disabled={preview === undefined || Number(preview.max_quotas) <= 0}
          onPick={(share) => preview && setQuotasText(quantityOfShare(preview.max_quotas, share, false))}
        />
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

type FundIssuanceCardProps = { fund: FundDetails };

/** Cartão da emissão no topo da página: preferência dos cotistas, sobra aberta ou encerrada, com o que já nasceu. */
export function FundIssuanceCard({ fund }: FundIssuanceCardProps) {
  const issuance = fund.issuance;
  if (issuance === null) return null;

  const closed = issuance.closed_on !== null;
  const preference = issuance.phase === "preference";
  const quotas = Number(issuance.quotas);
  const sold = Number(issuance.sold);
  const rights = issuance.my_rights === null ? null : Number(issuance.my_rights);
  const rightsLeft = rightsLeftOf(issuance);
  const rules = fund.issuance_rules;

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
          {!closed && preference && rights !== null && rightsLeft > 0 && (
            <>
              <p className="text-[13px]">
                <MetricLabel metric={PREFERENCE_RIGHT} />:{" "}
                <b className="font-mono font-semibold">{displayQuantity(String(rightsLeft))}</b> cotas
              </p>
              <p className="text-[13px] text-muted-foreground">
                Comprar as {displayQuantity(String(rights))} cotas do seu direito garante que a sua participação não cai
                com a emissão.
              </p>
              <SubscribeForm fundId={fund.id} issuance={issuance} rightsLeft={rightsLeft} />
            </>
          )}
          {!closed && preference && (rights === null || rightsLeft === 0) && (
            <p className="text-[13px] text-muted-foreground">
              {rights === null
                ? `Só quem tinha cotas no anúncio compra agora. Para você, a emissão abre em ${displayIsoDate(issuance.preference_ends_on)}.`
                : "Você já usou todo o seu direito de preferência. A sobra abre a todos depois da preferência."}
            </p>
          )}
          {!closed && !preference && (
            <p className="text-[13px] text-muted-foreground">
              A sobra está aberta: compre pelo livro de ofertas, ao preço fixo de {displayMoney(issuance.price)}.
            </p>
          )}
          {!closed && (
            <div className="grid gap-1 border-t pt-3 text-[13px] text-muted-foreground">
              <b className="font-semibold text-foreground">Quem compra e quando</b>
              <p>
                Preferência ({rules.preference_sessions} pregões): só os cotistas do anúncio, cada um até o seu direito.
              </p>
              <p>Sobra ({rules.leftover_sessions} pregões): qualquer jogador, pelo livro de ofertas, ao preço fixo.</p>
              <p>
                Bots cotistas: só no último pregão da sobra, e só se o preço da emissão couber no valor que dão à cota,
                que é o patrimônio por cota mais um prêmio de até ±{displayPercent(rules.bot_premium_limit, 0)} pelo
                desempenho acima do CDI, ou o ágio que a cota tinha antes do anúncio, o que for maior. Cada bot ainda
                varia a opinião em até ±{displayPercent(rules.bot_opinion_range, 0)}.
              </p>
              <p>
                Mercado: também no último pregão, depois dos jogadores e dos bots. Compra a fração da sobra que o
                desempenho acima do CDI ou o ágio pede, até a sobra inteira com{" "}
                {displayPercent(rules.bot_premium_limit, 0)}, e nada sem um dos dois.
              </p>
              {issuance.estimate && (
                <IssuanceEstimate
                  estimate={issuance.estimate}
                  decidesAt={`no último pregão da sobra, em ${displayIsoDate(issuance.ends_on)}`}
                />
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
