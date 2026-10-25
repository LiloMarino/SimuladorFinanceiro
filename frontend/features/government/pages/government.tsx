import { useState } from "react";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { GovernmentPanel, MeasureKind } from "@/types";
import { ApprovalCard } from "../components/approval-card";
import { FrozenPortfolioCard } from "../components/frozen-portfolio-card";
import { GovernmentHeader } from "../components/government-header";
import { BeforeFirstTerm, GovernmentError, GovernmentSkeleton } from "../components/government-states";
import { NewMeasureDialog } from "../components/new-measure-dialog";
import { QueueCard } from "../components/queue-card";
import { TaxesCard } from "../components/taxes-card";
import { lowStreakLabel, successionLabel } from "../lib/government";

export default function GovernmentPage() {
  usePageLabel("Governo");
  const { data: panel, error, refetch } = useGovernment();

  if (!panel) {
    return error ? <GovernmentError onRetry={() => void refetch()} /> : <GovernmentSkeleton />;
  }

  return <GovernmentContent panel={panel} />;
}

type Proposal = { kind?: MeasureKind };

function GovernmentContent({ panel }: { panel: GovernmentPanel }) {
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const approval = panel.approval;

  if (panel.computer_until_inauguration) return <BeforeFirstTerm />;

  return (
    <div className="grid gap-5">
      <GovernmentHeader panel={panel} />

      {panel.is_president && approval && approval.low_streak > 0 && (
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>{lowStreakLabel(approval)}</AlertTitle>
          <AlertDescription>
            Aprovação de {approval.value}% hoje. Mais um mês abaixo do piso e o impeachment tira você do governo, e{" "}
            {successionLabel(panel)}.
          </AlertDescription>
        </Alert>
      )}

      {/* Popularidade e impostos */}
      <div className="grid items-start gap-5 xl:grid-cols-2">
        <ApprovalCard panel={panel} />
        <TaxesCard panel={panel} onPropose={(kind) => setProposal({ kind })} />
      </div>

      {/* Fila do Congresso e carteira do presidente */}
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.9fr)_minmax(0,1fr)]">
        <QueueCard panel={panel} />
        <FrozenPortfolioCard panel={panel} />
      </div>

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
