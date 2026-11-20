import { useState } from "react";
import { Navigate, useParams, useSearchParams } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { Badge } from "@/shared/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { useFund } from "@/shared/hooks/queries/useFund";
import { useAuth } from "@/shared/hooks/useAuth";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { managerQuotasOf } from "@/shared/lib/fund-view";
import type { FundDetails } from "@/types";
import { ActionsTab } from "../components/tabs/actions-tab";
import { AssemblyTab } from "../components/tabs/assembly-tab";
import { IncomeTab } from "../components/tabs/income-tab";
import { OverviewTab } from "../components/tabs/overview-tab";
import { PortfolioTab } from "../components/tabs/portfolio-tab";
import { QuotasTab } from "../components/tabs/quotas-tab";
import { ReportTab } from "../components/tabs/report-tab";
import { SettingsTab } from "../components/tabs/settings-tab";
import { BuybackDialog } from "../components/buyback-dialog";
import { ComanagerInviteDialog } from "../components/comanager-invite-dialog";
import { ComanagerRemoveDialog } from "../components/comanager-remove-dialog";
import { ComanagerShareDialog } from "../components/comanager-share-dialog";
import { ContributeDialog } from "../components/contribute-dialog";
import { DirectedIssuanceDialog } from "../components/directed-issuance-dialog";
import { DistributionDialog } from "../components/distribution-dialog";
import { FeesDialog } from "../components/fees-dialog";
import { FundSkeleton } from "../components/fund-skeleton";
import { FundTop } from "../components/fund-top";
import { IssuanceDialog } from "../components/issuance-dialog";
import { MergeDialog } from "../components/merge-dialog";
import { OfferDialog } from "../components/offer-dialog";
import type { Comanager } from "../lib/fund-comanagers";
import { FIRST_QUOTA_PRICE } from "../lib/fund-math";
import { votesToCastOf } from "../lib/fund-assembly";
import { fundPending, fundPendingCount } from "../lib/fund-pending";
import {
  FUND_TAB_LABEL,
  tabFrom,
  visibleTabs,
  type FundDialog,
  type FundTab,
  type FundTabActions,
} from "../lib/fund-tabs";

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

type DetailsContentProps = { fund: FundDetails; userId: number };

function FundDetailsContent({ fund, userId }: DetailsContentProps) {
  usePageLabel(fund.name);
  // Só o gestor principal comanda a gestora; o co-gestor opera a carteira e o resto da sala é cotista
  const manager = fund.my_role === "manager";
  const [params, setParams] = useSearchParams();
  const [dialog, setDialog] = useState<FundDialog | null>(null);
  const [shareTarget, setShareTarget] = useState<Comanager | null>(null);
  const [removeTarget, setRemoveTarget] = useState<Comanager | null>(null);

  const tabs = visibleTabs(manager);
  const tab = tabFrom(params.get("tab"), tabs);
  const pendingCount = fundPendingCount(fundPending(fund, userId));
  const votesToCast = votesToCastOf(fund.assembly).length;
  const total = Number(fund.quotas);
  const nav = fund.nav === null ? FIRST_QUOTA_PRICE : Number(fund.nav);

  const goTo = (next: FundTab) => setParams({ tab: next }, { replace: true });
  const actions: FundTabActions = {
    open: setDialog,
    goTo,
    changeShare: setShareTarget,
    remove: setRemoveTarget,
  };
  const closeDialog = (open: boolean) => !open && setDialog(null);

  return (
    <div className="grid gap-5">
      <FundTop fund={fund} />

      <Tabs value={tab} onValueChange={(value: string) => goTo(tabFrom(value, tabs))}>
        <TabsList variant="line" accent="fund">
          {tabs.map((item) => (
            <TabsTrigger key={item} value={item}>
              {FUND_TAB_LABEL[item]}
              {item === "actions" && pendingCount > 0 && (
                <Badge variant="warning" size="sm" aria-label={`${pendingCount} decisões com prazo`}>
                  {pendingCount}
                </Badge>
              )}
              {item === "assembly" && votesToCast > 0 && (
                <Badge variant="warning" size="sm" aria-label={`${votesToCast} votações abertas`}>
                  {votesToCast}
                </Badge>
              )}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* O que o jogador decide e faz nesta gestora */}
        <TabsContent value="actions">
          <ActionsTab fund={fund} userId={userId} actions={actions} />
        </TabsContent>

        {/* Preço, retorno e composição */}
        <TabsContent value="overview">
          <OverviewTab fund={fund} actions={actions} />
        </TabsContent>

        {/* Carteira, só do gestor */}
        {manager && (
          <TabsContent value="portfolio">
            <PortfolioTab fund={fund} actions={actions} />
          </TabsContent>
        )}

        {/* Cotistas, ofertas e emissões */}
        <TabsContent value="quotas">
          <QuotasTab fund={fund} userId={userId} actions={actions} />
        </TabsContent>

        {/* Rendimentos pagos aos cotistas */}
        <TabsContent value="income">
          <IncomeTab fund={fund} actions={actions} manager={manager} />
        </TabsContent>

        {/* Votação para trocar o gestor */}
        <TabsContent value="assembly">
          <AssemblyTab fund={fund} actions={actions} />
        </TabsContent>

        {/* Relatório mensal */}
        <TabsContent value="report">
          <ReportTab fund={fund} />
        </TabsContent>

        {/* Taxas e parte distribuída, só do gestor */}
        {manager && (
          <TabsContent value="settings">
            <SettingsTab fund={fund} actions={actions} />
          </TabsContent>
        )}
      </Tabs>

      {manager && (
        <>
          <FeesDialog open={dialog === "fees"} onOpenChange={closeDialog} fund={fund} />
          <ComanagerInviteDialog open={dialog === "invite"} onOpenChange={closeDialog} fund={fund} />
          <ComanagerShareDialog comanager={shareTarget} onClose={() => setShareTarget(null)} fund={fund} />
          <ComanagerRemoveDialog comanager={removeTarget} onClose={() => setRemoveTarget(null)} fundId={fund.id} />
          <DistributionDialog open={dialog === "distribution"} onOpenChange={closeDialog} fund={fund} />
          <OfferDialog
            open={dialog === "offer"}
            onOpenChange={closeDialog}
            fundId={fund.id}
            fundName={fund.name}
            nav={nav}
            managerQuotas={managerQuotasOf(fund)}
            totalQuotas={total}
          />
          <IssuanceDialog
            open={dialog === "issuance"}
            onOpenChange={closeDialog}
            fundId={fund.id}
            fundName={fund.name}
            nav={nav}
            totalQuotas={total}
            rules={fund.issuance_rules}
          />
          <DirectedIssuanceDialog open={dialog === "directed"} onOpenChange={closeDialog} fund={fund} />
          <BuybackDialog open={dialog === "buyback"} onOpenChange={closeDialog} fund={fund} />
          <MergeDialog open={dialog === "merge"} onOpenChange={closeDialog} fund={fund} />
          <ContributeDialog
            open={dialog === "contribute"}
            onOpenChange={closeDialog}
            fundId={fund.id}
            fundName={fund.name}
            quotaPrice={total === 0 ? FIRST_QUOTA_PRICE : nav}
          />
        </>
      )}
    </div>
  );
}
