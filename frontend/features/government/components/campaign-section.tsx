import { useRef } from "react";
import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { ElectionPanel, ElectionParty } from "@/types";
import { useCampaign } from "../hooks/queries/useCampaign";
import { CampaignActionsCard } from "./campaign-actions-card";
import { CampaignBaseCard } from "./campaign-base-card";
import { CampaignHistoryCard } from "./campaign-history-card";
import { CampaignRecentCard } from "./campaign-recent-card";

type CampaignSectionProps = {
  panel: ElectionPanel;
  party: ElectionParty;
  cash: string | undefined;
  nickname: string;
  onChangeContribution: () => void;
};

/** As ações avulsas da campanha do partido: o cartão das ações, as últimas, a verba de base e o histórico. */
export function CampaignSection({ panel, party, cash, nickname, onChangeContribution }: CampaignSectionProps) {
  const { data: campaign, error, refetch } = useCampaign();
  const history = useRef<HTMLDivElement>(null);

  if (!campaign) {
    return (
      <CardState
        title="Ações de campanha"
        label="Carregando as ações de campanha"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar as ações"
        errorDescription="O resto da página continua valendo; só este cartão falhou."
      >
        <Skeleton className="h-3 w-3/5" />
        <div className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <Skeleton key={index} className="h-32" />
          ))}
        </div>
        {Array.from({ length: 4 }, (_, index) => (
          <div key={index} className="flex items-center gap-2.5">
            <Skeleton className="size-7" />
            <Skeleton className="h-3 w-2/5" />
            <span className="flex-1" />
            <Skeleton className="h-3 w-15" />
          </div>
        ))}
      </CardState>
    );
  }

  return (
    <div className="grid gap-5">
      <CampaignActionsCard campaign={campaign} groups={panel.groups} cash={cash} />
      <div className="grid items-start gap-5 lg:grid-cols-2">
        <CampaignRecentCard
          campaign={campaign}
          party={party}
          onHistory={() => history.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
        />
        <CampaignBaseCard
          campaign={campaign}
          party={party}
          nickname={nickname}
          onChangeContribution={onChangeContribution}
        />
      </div>
      <div ref={history} className="scroll-mt-4">
        <CampaignHistoryCard campaign={campaign} party={party} nickname={nickname} />
      </div>
    </div>
  );
}
