import { useState } from "react";
import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { GovernmentPanel, StateCompaniesPanel } from "@/types";
import { useStateCompanies } from "../../hooks/queries/useStateCompanies";
import { useToday } from "../../hooks/useToday";
import { CommandStateCompanyDialog } from "./command-state-company-dialog";
import { FoundStateCompanyDialog } from "./found-state-company-dialog";
import { PrivatizationOfferCard } from "./privatization-offer-card";
import { PrivatizeDialog } from "./privatize-dialog";
import { StateCompaniesSummary } from "./state-companies-summary";
import { StateCompaniesTable } from "./state-companies-table";
import { StateMovementsCard } from "./state-movements-card";

type StateCompaniesTabProps = {
  panel: GovernmentPanel;
  /** Leva à aba do Congresso, onde a votação da privatização aparece */
  onSeeVote: () => void;
};

/** A aba Estatais: a consulta se resolve aqui e o conteúdo recebe o painel pronto. */
export function StateCompaniesTab({ panel, onSeeVote }: StateCompaniesTabProps) {
  const { data, error, refetch } = useStateCompanies();

  if (!data) {
    return (
      <div className="pt-3">
        <CardState
          bare
          label="Carregando as estatais"
          error={error}
          onRetry={() => void refetch()}
          errorTitle="Não deu para carregar as estatais"
        >
          <Skeleton className="h-28" />
          <Skeleton className="h-64" />
          <Skeleton className="h-40" />
        </CardState>
      </div>
    );
  }

  return <StateCompaniesContent government={panel} state={data} onSeeVote={onSeeVote} />;
}

type StateCompaniesContentProps = {
  government: GovernmentPanel;
  state: StateCompaniesPanel;
  onSeeVote: () => void;
};

type Dialog = { kind: "found" } | { kind: "command" | "privatize"; ticker: string };

function StateCompaniesContent({ government, state, onSeeVote }: StateCompaniesContentProps) {
  const today = useToday(government);
  const [dialog, setDialog] = useState<Dialog | null>(null);
  const closeDialog = () => setDialog(null);

  const privatizing =
    dialog?.kind === "privatize" ? state.companies.find((c) => c.ticker === dialog.ticker) : undefined;

  return (
    <div className="grid gap-5 pt-3">
      <StateCompaniesSummary panel={state} />

      {/* Ofertas de privatização abertas à sala */}
      {state.offers.map((offer) => (
        <PrivatizationOfferCard key={offer.ticker} offer={offer} today={today} />
      ))}

      <StateCompaniesTable
        panel={state}
        queue={government.queue}
        onFound={() => setDialog({ kind: "found" })}
        onCommand={(ticker) => setDialog({ kind: "command", ticker })}
        onPrivatize={(ticker) => setDialog({ kind: "privatize", ticker })}
        onSeeVote={onSeeVote}
      />

      <StateMovementsCard movements={state.movements} />

      {/* Diálogos */}
      <FoundStateCompanyDialog
        open={dialog?.kind === "found"}
        onOpenChange={(open) => !open && closeDialog()}
        companies={state.companies}
        rules={state.rules}
        vigenceDays={government.vigence_days}
      />
      {dialog?.kind === "command" && (
        <CommandStateCompanyDialog ticker={dialog.ticker} today={today} onClose={closeDialog} />
      )}
      {privatizing && (
        <PrivatizeDialog company={privatizing} offerSessions={state.rules.offer_sessions} onClose={closeDialog} />
      )}
    </div>
  );
}
