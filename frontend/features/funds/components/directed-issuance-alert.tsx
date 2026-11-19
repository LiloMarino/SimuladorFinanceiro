import { Handshake } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayIsoDate, displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useAnswerDirectedIssuance } from "../hooks/mutations/useAnswerDirectedIssuance";
import { useCancelDirectedIssuance } from "../hooks/mutations/useCancelDirectedIssuance";
import { useFundDirectedIssuancePreview } from "../hooks/queries/useFundDirectedIssuancePreview";
import type { DirectedOffer } from "../lib/fund-directed";

type DirectedIssuanceAlertProps = {
  fund: FundDetails;
  offer: DirectedOffer;
  /** Quem consulta é o co-gestor a quem a oferta foi feita */
  isBuyer: boolean;
};

/** A oferta de cotas novas que espera resposta: o co-gestor aceita ou recusa, o gestor principal cancela. */
export function DirectedIssuanceAlert({ fund, offer, isBuyer }: DirectedIssuanceAlertProps) {
  const quotas = displayQuantity(offer.quotas);
  const validity = offer.expires_on ? ` A oferta vale até ${displayIsoDate(offer.expires_on)}.` : "";

  return (
    <Alert variant="info">
      <Handshake />
      {isBuyer ? (
        <BuyerOffer fund={fund} offer={offer} quotas={quotas} validity={validity} />
      ) : (
        <PrincipalOffer fund={fund} offer={offer} quotas={quotas} validity={validity} />
      )}
    </Alert>
  );
}

type OfferBodyProps = {
  fund: FundDetails;
  offer: DirectedOffer;
  quotas: string;
  validity: string;
};

function BuyerOffer({ fund, offer, quotas, validity }: OfferBodyProps) {
  const answer = useAnswerDirectedIssuance(fund.id);
  // O preço de hoje é a referência; o da compra vale no momento em que o co-gestor aceita
  const { data: preview } = useFundDirectedIssuancePreview(fund.id, Number(offer.quotas));

  return (
    <>
      <AlertTitle>
        {fund.manager_nickname} oferece {quotas} cotas novas de {fund.name}
      </AlertTitle>
      <AlertDescription>
        <div className="grid gap-3">
          <p>
            {preview
              ? `Hoje cada cota sairia a ${displayMoney(preview.price)}, num total de ${displayMoney(preview.cost)} do seu caixa pessoal.`
              : "Carregando o preço de hoje."}{" "}
            O preço e o teto valem no momento em que você aceita.{validity}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="fund" size="sm" disabled={answer.isPending} onClick={() => answer.mutate(true)}>
              {answer.isPending && <Spinner />}
              Aceitar
            </Button>
            <Button variant="outline" size="sm" disabled={answer.isPending} onClick={() => answer.mutate(false)}>
              Recusar
            </Button>
          </div>
        </div>
      </AlertDescription>
    </>
  );
}

function PrincipalOffer({ fund, offer, quotas, validity }: OfferBodyProps) {
  const cancel = useCancelDirectedIssuance(fund.id);

  return (
    <>
      <AlertTitle>
        Oferta de {quotas} cotas novas para {offer.buyer_nickname}
      </AlertTitle>
      <AlertDescription>
        <div className="grid gap-3">
          <p>
            Esperando a resposta de {offer.buyer_nickname}.{validity}
          </p>
          <div>
            <Button variant="outline" size="sm" disabled={cancel.isPending} onClick={() => cancel.mutate()}>
              {cancel.isPending && <Spinner />}
              Cancelar oferta
            </Button>
          </div>
        </div>
      </AlertDescription>
    </>
  );
}
