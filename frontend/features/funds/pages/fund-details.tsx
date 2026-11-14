import { Lock } from "lucide-react";
import { useRef, useState } from "react";
import { Navigate, useParams } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useAuth } from "@/shared/hooks/useAuth";
import usePageLabel from "@/shared/hooks/usePageLabel";
import {
  displayIsoDate,
  displayMoney,
  displayPercent,
  displayQuantity,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { ContributeDialog } from "../components/contribute-dialog";
import { FeesDialog } from "../components/fees-dialog";
import { FundComposition } from "../components/fund-composition";
import { FundFeesCard } from "../components/fund-fees-card";
import { FundHeader } from "../components/fund-header";
import { FundHolders } from "../components/fund-holders";
import { FundMetricsRow } from "../components/fund-metrics-row";
import { FundMovements } from "../components/fund-movements";
import { FundOfferCard } from "../components/fund-offer-card";
import { FundOrderPanel } from "../components/fund-order-panel";
import { FundPriceChart } from "../components/fund-price-chart";
import { FundSkeleton } from "../components/fund-skeleton";
import { OfferDialog } from "../components/offer-dialog";
import { useCloseFundOffer } from "../hooks/mutations/useCloseFundOffer";
import { useFund } from "../hooks/queries/useFund";
import { FIRST_QUOTA_PRICE } from "../lib/fund-math";
import { fundStage, managerQuotasOf, managerShareOf } from "../lib/fund-view";

export default function FundDetailsPage() {
  const id = Number(useParams().fundId);
  return Number.isInteger(id) && id > 0 ? <FundDetailsLoader id={id} /> : <Navigate to="/funds" replace />;
}

/** Resolve a gestora e o jogador e entrega a página já com eles. */
function FundDetailsLoader({ id }: { id: number }) {
  const { data: fund, error, refetch } = useFund(id);
  const { user } = useAuth();

  if (!fund || user === null) {
    return (
      <CardState
        bare
        label="Carregando a gestora"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar a gestora"
      >
        <FundSkeleton />
      </CardState>
    );
  }

  return <FundDetailsContent fund={fund} viewer={fund.manager_user_id !== user.id} />;
}

/** "Você tem X% · N cotas · R$ hoje · retorno": a posição de quem olha a gestora de fora. */
function MyHoldingStrip({ fund }: { fund: FundDetails }) {
  const total = Number(fund.quotas);
  const mine = Number(fund.my_quotas);
  if (mine <= 0) return null;

  return (
    <p className="rounded-lg bg-fund-soft px-4 py-2.5 text-[13px]">
      Você tem <b className="font-mono font-semibold">{displayPercent(total > 0 ? mine / total : 0, 1)}</b> ·{" "}
      <span className="font-mono">{displayQuantity(fund.my_quotas)}</span> cotas ·{" "}
      <span className="font-mono">{displayMoney(fund.my_value)}</span> hoje ·{" "}
      {fund.my_return === null ? "sem retorno ainda" : `retorno de ${displaySignedPercent(fund.my_return, 1)}`}
    </p>
  );
}

type DetailsContentProps = { fund: FundDetails; viewer: boolean };

function FundDetailsContent({ fund, viewer }: DetailsContentProps) {
  usePageLabel(fund.name);
  const [feesOpen, setFeesOpen] = useState(false);
  const [offerOpen, setOfferOpen] = useState(false);
  const [contributeOpen, setContributeOpen] = useState(false);
  const quantityRef = useRef<HTMLInputElement>(null);
  const { fund: activeFund, switchAccount } = useActiveAccount();
  const closeOffer = useCloseFundOffer(fund.id);

  const stage = fundStage(fund);
  const managerQuotas = managerQuotasOf(fund);
  const managerShare = managerShareOf(fund);
  const total = Number(fund.quotas);
  const empty = stage === "closed" && total === 0;
  const operating = activeFund?.fund_id === fund.id;
  const nav = fund.nav === null ? FIRST_QUOTA_PRICE : Number(fund.nav);

  const buyInOffer = () => {
    quantityRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    quantityRef.current?.focus();
  };

  const managerActions = (
    <>
      {stage === "closed" && (
        <Button variant="outline" onClick={() => setContributeOpen(true)}>
          Levar da carteira
        </Button>
      )}
      {stage !== "offer" && (
        <Button variant="outline" disabled={total === 0} onClick={() => setOfferOpen(true)}>
          Oferta pública
        </Button>
      )}
      <Button variant="outline" onClick={() => setFeesOpen(true)}>
        Taxas
      </Button>
      {operating ? (
        <Button variant="outline" onClick={() => switchAccount(null)}>
          Voltar à minha carteira
        </Button>
      ) : (
        <Button variant="fund" onClick={() => switchAccount(fund.id)}>
          Operar a carteira da gestora
        </Button>
      )}
    </>
  );

  const offerAction =
    stage !== "offer" ? undefined : viewer ? (
      <Button variant="fund" size="sm" onClick={buyInOffer}>
        Comprar na oferta
      </Button>
    ) : (
      <Button variant="outline" size="sm" disabled={closeOffer.isPending} onClick={() => closeOffer.mutate()}>
        {closeOffer.isPending && <Spinner />}
        Encerrar a oferta
      </Button>
    );

  return (
    <>
      {/* Cabeçalho */}
      <FundHeader
        fund={fund}
        subtitle={
          viewer
            ? `Gerida por ${fund.manager_nickname ?? "—"}, que controla ${displayPercent(managerShare, 1)} das cotas`
            : `Você gere esta gestora e controla ${displayPercent(managerShare, 1)} das cotas`
        }
        actions={viewer ? undefined : managerActions}
        footer={viewer ? <MyHoldingStrip fund={fund} /> : undefined}
      />

      {/* Carteira congelada */}
      {fund.frozen_until && !viewer && (
        <Alert variant="warning">
          <Lock />
          <AlertTitle>A carteira está congelada</AlertTitle>
          <AlertDescription>
            A gestora não opera até {displayIsoDate(fund.frozen_until)}: as ordens da carteira dela ficam travadas até
            lá.
          </AlertDescription>
        </Alert>
      )}

      {/* Gestora fundada junto com a sala */}
      {empty && !viewer && (
        <Card variant="info">
          <CardContent>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="grid gap-1">
                <b className="text-[15px] font-semibold">A gestora nasceu com a sala e está vazia</b>
                <p className="max-w-2xl text-[13px] text-muted-foreground">
                  No primeiro dia ela não tem caixa nem cotas. Leve caixa e ações da sua carteira para receber as
                  primeiras cotas, a R$ 100,00 cada.
                </p>
              </div>
              <Button variant="fund" onClick={() => setContributeOpen(true)}>
                Levar da carteira
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Oferta pública */}
      <FundOfferCard fund={fund} action={offerAction} />

      {empty ? (
        <div className="grid items-start gap-5 xl:grid-cols-2">
          {!viewer && <FundFeesCard fund={fund} onChange={() => setFeesOpen(true)} />}
          <FundMovements movements={fund.movements} />
        </div>
      ) : (
        <>
          {/* Cinco números */}
          <FundMetricsRow fund={fund} viewer={viewer} />

          {/* Gráfico e boleta ou taxas */}
          <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
            <FundPriceChart fund={fund} />
            {viewer ? (
              <FundOrderPanel fund={fund} viewer quantityRef={quantityRef} />
            ) : (
              <FundFeesCard fund={fund} onChange={() => setFeesOpen(true)} />
            )}
          </div>

          {/* Carteira e cotistas */}
          <div className="grid items-start gap-5 xl:grid-cols-2">
            <FundComposition fund={fund} />
            <FundHolders fund={fund} viewer={viewer} />
          </div>

          {/* Movimentos e venda do gestor */}
          <div className={viewer ? "grid gap-5" : "grid items-start gap-5 xl:grid-cols-2"}>
            <FundMovements movements={fund.movements} />
            {!viewer && <FundOrderPanel fund={fund} viewer={false} />}
          </div>
        </>
      )}

      {!viewer && (
        <>
          <FeesDialog open={feesOpen} onOpenChange={setFeesOpen} fund={fund} />
          <OfferDialog
            open={offerOpen}
            onOpenChange={setOfferOpen}
            fundId={fund.id}
            fundName={fund.name}
            nav={nav}
            managerQuotas={managerQuotas}
            totalQuotas={total}
          />
          <ContributeDialog
            open={contributeOpen}
            onOpenChange={setContributeOpen}
            fundId={fund.id}
            fundName={fund.name}
            quotaPrice={total === 0 ? FIRST_QUOTA_PRICE : nav}
          />
        </>
      )}
    </>
  );
}
