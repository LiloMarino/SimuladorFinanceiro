import { useRef } from "react";
import type { ElectionPanel, ElectionParty } from "@/types";
import { useCampaign } from "../hooks/queries/useCampaign";
import { CampaignActionsCard } from "./campaign-actions-card";
import { CampaignBaseCard } from "./campaign-base-card";
import { CampaignHistoryCard } from "./campaign-history-card";
import { CampaignRecentCard } from "./campaign-recent-card";
import { CampaignError, CampaignSkeleton } from "./campaign-states";

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
    return error ? <CampaignError onRetry={() => void refetch()} /> : <CampaignSkeleton />;
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
