import { Clock, History, Info, Megaphone } from "lucide-react";
import { Card } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { ErrorState } from "@/shared/components/error-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useFundOffers } from "@/shared/hooks/queries/useFundOffers";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { FundOffers } from "@/types";
import { ClosedOffersTable } from "../components/closed-offers-table";
import { OpenOfferCard, type OfferWallet } from "../components/open-offer-card";
import { OffersSection } from "../components/offers-section";
import { PreferenceOfferRow } from "../components/preference-offer-row";

/** Quem compra: a carteira pessoal (com o caixa dela, quando já chegou) ou a de uma gestora, de onde a compra não sai. */
function useOfferWallet(): OfferWallet {
  const { accounts, fund, switchAccount } = useActiveAccount();
  if (fund !== null) return { kind: "fund", onUsePersonal: () => switchAccount(null) };
  const personal = accounts?.find((account) => account.fund_id === null);
  return { kind: "personal", cash: personal ? Number(personal.cash) : null };
}

function OffersSkeleton() {
  return (
    <Card aria-busy="true" aria-label="Carregando as ofertas">
      <Skeleton className="h-4.5 w-50" />
      <Skeleton className="h-45" />
    </Card>
  );
}

function OpenOffersEmpty() {
  return (
    <Card>
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="muted">
            <Megaphone />
          </EmptyMedia>
          <EmptyTitle>Nenhuma oferta aberta agora</EmptyTitle>
          <EmptyDescription>
            Quando uma gestora abrir oferta ou emissão, ela aparece aqui e sai no jornal. As encerradas seguem logo
            abaixo.
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    </Card>
  );
}

/** As ofertas já carregadas, em três blocos: a preferência de quem consulta, as abertas a todos e as encerradas. */
function OffersBody({ offers }: { offers: FundOffers }) {
  const wallet = useOfferWallet();
  const { preference, open, closed } = offers;

  return (
    <>
      {/* Sua preferência */}
      {preference.length > 0 && (
        <OffersSection
          icon={Clock}
          tone="warning"
          title="Sua preferência"
          count={preference.length}
          hint="Na emissão, quem já é cotista compra primeiro, até a parte que tem."
        >
          {preference.map((offer) => (
            <PreferenceOfferRow key={offer.fund_id} offer={offer} />
          ))}
        </OffersSection>
      )}

      {/* Abertas a qualquer investidor */}
      {open.length > 0 ? (
        <OffersSection
          icon={Megaphone}
          tone="fund"
          title="Abertas a qualquer investidor"
          count={open.length}
          hint="Oferta pública inicial de gestora nova e sobra de emissão."
        >
          <div className="grid gap-4 px-5">
            {open.map((offer) => (
              <OpenOfferCard key={`${offer.fund_id}-${offer.kind}`} offer={offer} wallet={wallet} />
            ))}
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Info className="size-3.5 shrink-0" />A sobra de uma emissão, depois da preferência dos cotistas, também
              aparece aqui
            </p>
          </div>
        </OffersSection>
      ) : (
        <OpenOffersEmpty />
      )}

      {/* Encerradas */}
      {closed.length > 0 && (
        <OffersSection
          icon={History}
          tone="muted"
          title="Encerradas"
          count={closed.length}
          hint="Quanto a cota vale hoje no mercado, perto do preço que se pagou na oferta."
        >
          <ClosedOffersTable offers={closed} />
        </OffersSection>
      )}
    </>
  );
}

/** A página Ofertas públicas: as vendas de cotas novas das gestoras, a preço fixo e por tempo limitado. */
export default function FundOffersPage() {
  usePageLabel("Ofertas públicas");
  const { data: offers, error, refetch } = useFundOffers();

  return (
    <>
      {/* Cabeçalho */}
      <header className="grid gap-1">
        <h1 className="text-2xl font-bold">Ofertas públicas</h1>
        <p className="text-[13px] text-muted-foreground">
          Cotas novas vendidas pela própria gestora, a preço fixo e por tempo limitado. A compra sai pelo detalhe da
          cota, na renda variável.
        </p>
      </header>

      {offers ? (
        <OffersBody offers={offers} />
      ) : error ? (
        <Card>
          <ErrorState
            title="Não deu para carregar as ofertas"
            description="A conexão com a sala caiu. Compras já feitas seguem valendo."
            error={error}
            onRetry={() => void refetch()}
          />
        </Card>
      ) : (
        <OffersSkeleton />
      )}
    </>
  );
}
