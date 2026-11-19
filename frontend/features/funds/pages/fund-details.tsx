import { Gavel, Lock } from "lucide-react";
import { useRef, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
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
import { ComanagerInviteAlert } from "../components/comanager-invite-alert";
import { ComanagerInviteDialog } from "../components/comanager-invite-dialog";
import { ComanagerRemoveDialog } from "../components/comanager-remove-dialog";
import { ComanagerShareDialog } from "../components/comanager-share-dialog";
import { ContributeDialog } from "../components/contribute-dialog";
import { BuybackDialog } from "../components/buyback-dialog";
import { DistributionDialog } from "../components/distribution-dialog";
import { FeesDialog } from "../components/fees-dialog";
import { FundAssembly } from "../components/fund-assembly";
import { FundBuybackCard } from "../components/fund-buyback-card";
import { FundComposition } from "../components/fund-composition";
import { FundDistributionsCard } from "@/shared/components/fund-distributions-card";
import { FundFeesCard } from "../components/fund-fees-card";
import { FundHeader } from "../components/fund-header";
import { FundHolders } from "../components/fund-holders";
import { FundIssuanceCard } from "../components/fund-issuance-card";
import { FundManagersCard } from "../components/fund-managers-card";
import { FundMetricsRow } from "@/shared/components/fund-metrics-row";
import { FundMovements } from "../components/fund-movements";
import { FundOfferCard } from "../components/fund-offer-card";
import { FundPriceChart } from "../components/fund-price-chart";
import { FundSkeleton } from "../components/fund-skeleton";
import { DirectedIssuanceAlert } from "../components/directed-issuance-alert";
import { DirectedIssuanceDialog } from "../components/directed-issuance-dialog";
import { IssuanceDialog } from "../components/issuance-dialog";
import { OfferDialog } from "../components/offer-dialog";
import { useCloseFundOffer } from "../hooks/mutations/useCloseFundOffer";
import { useFund } from "@/shared/hooks/queries/useFund";
import { myInviteOf, type Comanager } from "../lib/fund-comanagers";
import { FIRST_QUOTA_PRICE } from "../lib/fund-math";
import { fundStage, managerQuotasOf, managerShareOf } from "@/shared/lib/fund-view";

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

  return <FundDetailsContent fund={fund} userId={user.id} />;
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

type DetailsContentProps = { fund: FundDetails; userId: number };

function FundDetailsContent({ fund, userId }: DetailsContentProps) {
  usePageLabel(fund.name);
  // Só o gestor principal comanda a gestora; o co-gestor opera a carteira e o resto da sala é cotista
  const viewer = fund.my_role !== "manager";
  const comanager = fund.my_role === "comanager";
  const invite = myInviteOf(fund, userId);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [shareTarget, setShareTarget] = useState<Comanager | null>(null);
  const [removeTarget, setRemoveTarget] = useState<Comanager | null>(null);
  const [feesOpen, setFeesOpen] = useState(false);
  const [distributionOpen, setDistributionOpen] = useState(false);
  const [offerOpen, setOfferOpen] = useState(false);
  const [issuanceOpen, setIssuanceOpen] = useState(false);
  const [directedOpen, setDirectedOpen] = useState(false);
  const [buybackOpen, setBuybackOpen] = useState(false);
  const [contributeOpen, setContributeOpen] = useState(false);
  const assemblyRef = useRef<HTMLDivElement>(null);
  const { fund: activeFund, switchAccount } = useActiveAccount();
  const closeOffer = useCloseFundOffer(fund.id);
  const navigate = useNavigate();
  const directedOffer = fund.directed_issuance;

  const stage = fundStage(fund);
  const managerQuotas = managerQuotasOf(fund);
  const managerShare = managerShareOf(fund);
  const total = Number(fund.quotas);
  const empty = stage === "closed" && total === 0;
  const operating = activeFund?.fund_id === fund.id;
  const nav = fund.nav === null ? FIRST_QUOTA_PRICE : Number(fund.nav);
  const issuanceOpenNow = fund.issuance !== null && fund.issuance.closed_on === null;
  const buybackOpenNow = fund.buyback?.state === "open";
  const assemblyOpenNow = fund.assembly.current !== null;
  const voting = fund.assembly.current?.status === "VOTING";

  // A cota é negociada no detalhe do ativo, pelo livro e pela boleta
  const tradeLink = <Link to={`/variable-income/${fund.ticker}`} />;

  const operateButton = operating ? (
    <Button variant="outline" onClick={() => switchAccount(null)}>
      Voltar à minha carteira
    </Button>
  ) : (
    <Button variant="fund" onClick={() => switchAccount(fund.id)}>
      Operar a carteira da gestora
    </Button>
  );

  const managerActions = (
    <>
      {stage === "closed" && (
        <Button variant="outline" onClick={() => setContributeOpen(true)}>
          Levar da carteira
        </Button>
      )}
      {stage === "closed" && (
        <Button variant="outline" disabled={total === 0} onClick={() => setOfferOpen(true)}>
          Oferta pública
        </Button>
      )}
      {stage === "listed" && (
        <>
          <Button
            variant="outline"
            disabled={total === 0 || issuanceOpenNow || buybackOpenNow || assemblyOpenNow}
            onClick={() => setIssuanceOpen(true)}
          >
            Emitir cotas
          </Button>
          <Button
            variant="outline"
            disabled={total === 0 || issuanceOpenNow || buybackOpenNow}
            onClick={() => setBuybackOpen(true)}
          >
            Recomprar
          </Button>
          <Button
            variant="outline"
            disabled={total === 0 || directedOffer !== null || issuanceOpenNow || buybackOpenNow || assemblyOpenNow}
            onClick={() => setDirectedOpen(true)}
          >
            Emissão dirigida
          </Button>
        </>
      )}
      {stage !== "closed" && (
        <Button variant="outline" nativeButton={false} render={tradeLink}>
          Vender cotas
        </Button>
      )}
      <Button variant="outline" onClick={() => setFeesOpen(true)}>
        Taxas
      </Button>
      {stage === "listed" && (
        <Button
          variant="outline"
          onClick={() => {
            switchAccount(fund.id);
            void navigate("/credit");
          }}
        >
          Pedir empréstimo
        </Button>
      )}
      {operateButton}
    </>
  );

  const viewerActions =
    stage === "listed" ? (
      <Button variant="outline" nativeButton={false} render={tradeLink}>
        Negociar cotas
      </Button>
    ) : undefined;

  const offerAction =
    stage !== "offer" ? undefined : viewer ? (
      <Button variant="fund" size="sm" nativeButton={false} render={tradeLink}>
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
          comanager
            ? `Gerida por ${fund.manager_nickname ?? "—"}, que controla ${displayPercent(managerShare, 1)} das cotas · você é co-gestor, com ${displayPercent(Number(fund.my_share ?? 0), 0)} das taxas`
            : viewer
              ? `Gerida por ${fund.manager_nickname ?? "—"}, que controla ${displayPercent(managerShare, 1)} das cotas`
              : `Você gere esta gestora e controla ${displayPercent(managerShare, 1)} das cotas`
        }
        actions={comanager ? operateButton : viewer ? viewerActions : managerActions}
        footer={viewer ? <MyHoldingStrip fund={fund} /> : undefined}
      />

      {/* Convite para co-gestor */}
      {invite && <ComanagerInviteAlert fund={fund} invite={invite} />}

      {/* Oferta de emissão dirigida */}
      {directedOffer && (
        <DirectedIssuanceAlert fund={fund} offer={directedOffer} isBuyer={directedOffer.buyer_user_id === userId} />
      )}

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

      {/* Defesa do gestor durante a votação */}
      {voting && !viewer && (
        <Alert variant="destructive">
          <Gavel />
          <AlertTitle>Há uma assembleia para trocar você da gestão</AlertTitle>
          <AlertDescription>
            <div className="grid gap-3">
              <p>
                O voto pesa pelas cotas no fechamento do último pregão, e você conta contra com as suas. Recomprar cotas
                dos outros cotistas tira o peso deles do placar.
              </p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => assemblyRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
                >
                  Ver a votação
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={total === 0 || buybackOpenNow}
                  onClick={() => setBuybackOpen(true)}
                >
                  Recomprar
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Assembleia */}
      <div ref={assemblyRef}>
        <FundAssembly fund={fund} />
      </div>

      {/* Oferta pública */}
      <FundOfferCard fund={fund} action={offerAction} />

      {/* Emissão de cotas */}
      <FundIssuanceCard fund={fund} viewer={viewer} />

      {/* Recompra */}
      <FundBuybackCard fund={fund} viewer={viewer} />

      {/* Gestores */}
      {(!viewer || fund.comanagers.length > 0) && (
        <FundManagersCard
          fund={fund}
          {...(viewer
            ? {}
            : {
                actions: {
                  onInvite: () => setInviteOpen(true),
                  onChangeShare: setShareTarget,
                  onRemove: setRemoveTarget,
                },
              })}
        />
      )}

      {empty ? (
        <div className="grid items-start gap-5 xl:grid-cols-2">
          {!viewer && <FundFeesCard fund={fund} onChange={() => setFeesOpen(true)} />}
          <FundMovements movements={fund.movements} />
        </div>
      ) : (
        <>
          {/* Números do topo */}
          <FundMetricsRow fund={fund} viewer={viewer} />

          {/* Gráfico e taxas */}
          {viewer ? (
            <FundPriceChart fund={fund} />
          ) : (
            <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
              <FundPriceChart fund={fund} />
              <FundFeesCard fund={fund} onChange={() => setFeesOpen(true)} />
            </div>
          )}

          {/* Carteira e cotistas */}
          <div className="grid items-start gap-5 xl:grid-cols-2">
            <FundComposition fund={fund} />
            <FundHolders fund={fund} viewer={viewer} />
          </div>

          {/* Rendimentos */}
          <FundDistributionsCard fund={fund} {...(viewer ? {} : { onChange: () => setDistributionOpen(true) })} />

          {/* Movimentos */}
          <FundMovements movements={fund.movements} />
        </>
      )}

      {!viewer && (
        <>
          <FeesDialog open={feesOpen} onOpenChange={setFeesOpen} fund={fund} />
          <ComanagerInviteDialog open={inviteOpen} onOpenChange={setInviteOpen} fund={fund} />
          <ComanagerShareDialog comanager={shareTarget} onClose={() => setShareTarget(null)} fund={fund} />
          <ComanagerRemoveDialog comanager={removeTarget} onClose={() => setRemoveTarget(null)} fundId={fund.id} />
          <DistributionDialog open={distributionOpen} onOpenChange={setDistributionOpen} fund={fund} />
          <OfferDialog
            open={offerOpen}
            onOpenChange={setOfferOpen}
            fundId={fund.id}
            fundName={fund.name}
            nav={nav}
            managerQuotas={managerQuotas}
            totalQuotas={total}
          />
          <IssuanceDialog
            open={issuanceOpen}
            onOpenChange={setIssuanceOpen}
            fundId={fund.id}
            fundName={fund.name}
            nav={nav}
            totalQuotas={total}
          />
          <DirectedIssuanceDialog open={directedOpen} onOpenChange={setDirectedOpen} fund={fund} />
          <BuybackDialog
            open={buybackOpen}
            onOpenChange={setBuybackOpen}
            fundId={fund.id}
            fundName={fund.name}
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
