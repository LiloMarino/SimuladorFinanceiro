import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { GovernmentPanel, MeasureKind } from "@/types";
import { AccountsTab } from "../components/accounts-tab";
import { ApprovalCard } from "../components/approval-card";
import { FrozenPortfolioCard } from "../components/frozen-portfolio-card";
import { GovernmentHeader } from "../components/government-header";
import { ImpeachmentAlert } from "../components/impeachment-alert";
import { CongressTab } from "../components/congress-tab";
import { BeforeFirstTerm, GovernmentError, GovernmentSkeleton } from "../components/government-states";
import { NewMeasureDialog } from "../components/new-measure-dialog";
import { TermPromisesCard } from "../components/term-promises-card";
import { unguidedCount } from "../lib/house";

export default function GovernmentPage() {
  usePageLabel("Governo");
  const { data: panel, error, refetch } = useGovernment();

  if (!panel) {
    return error ? <GovernmentError onRetry={() => void refetch()} /> : <GovernmentSkeleton />;
  }

  return <GovernmentContent panel={panel} />;
}

type Proposal = { kind?: MeasureKind | undefined };

const TABS = ["mandate", "accounts", "congress"] as const;
type Tab = (typeof TABS)[number];

/** A aba vem do endereço (?tab=); sem ela ou com valor desconhecido, abre o Mandato. */
function tabFrom(value: string | null): Tab {
  return TABS.find((tab) => tab === value) ?? "mandate";
}

function GovernmentContent({ panel }: { panel: GovernmentPanel }) {
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [params, setParams] = useSearchParams();
  const tab = tabFrom(params.get("tab"));
  const unguided = unguidedCount(panel.congress, panel.queue);

  if (panel.computer_until_inauguration) return <BeforeFirstTerm />;

  return (
    <div className="grid gap-5">
      <GovernmentHeader panel={panel} />

      {/* Aviso de impeachment, só para o presidente */}
      {panel.is_president && <ImpeachmentAlert panel={panel} />}

      <Tabs value={tab} onValueChange={(value: string) => setParams({ tab: tabFrom(value) }, { replace: true })}>
        <TabsList variant="line">
          <TabsTrigger value="mandate">Mandato</TabsTrigger>
          <TabsTrigger value="accounts">Contas</TabsTrigger>
          <TabsTrigger value="congress">
            Congresso
            {unguided > 0 && (
              <Badge variant="warning" size="sm" aria-label={`${unguided} votações sem orientação`}>
                {unguided}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Aprovação, promessas da chapa e carteira do presidente */}
        <TabsContent value="mandate">
          <div className="grid gap-5 pt-3">
            <ApprovalCard panel={panel} />
            {panel.promises && <TermPromisesCard promises={panel.promises} termEnd={panel.term_end} />}
            <FrozenPortfolioCard panel={panel} />
          </div>
        </TabsContent>

        {/* Orçamento do país e impostos */}
        <TabsContent value="accounts">
          <div className="pt-3">
            <AccountsTab panel={panel} onPropose={(kind) => setProposal({ kind })} />
          </div>
        </TabsContent>

        {/* Fila do Congresso */}
        <TabsContent value="congress">
          <CongressTab panel={panel} />
        </TabsContent>
      </Tabs>

      {panel.is_president && (
        <NewMeasureDialog
          open={proposal !== null}
          onOpenChange={(open) => !open && setProposal(null)}
          panel={panel}
          initialKind={proposal?.kind}
        />
      )}
    </div>
  );
}
