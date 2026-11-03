import { useRef } from "react";
import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { ElectionPanel, ElectionParty } from "@/types";
import { useCampaign } from "../hooks/queries/useCampaign";
import { partyOrder } from "../lib/voters";
import { CampaignActionsCard } from "./campaign-actions-card";
import { CampaignHistoryCard } from "./campaign-history-card";
import { ElectorateCard } from "./electorate-card";
import { MyPartyCard } from "./my-party-card";

type CampaignSectionProps = {
  panel: ElectionPanel;
  party: ElectionParty;
  cash: string | undefined;
  nickname: string;
  onEditTicket: () => void;
  onEditPromises: () => void;
  onChangeContribution: () => void;
  onExpel: (nickname: string) => void;
  onLeave: () => void;
};

/** A aba da campanha, cada informação num cartão só: ações, eleitorado, histórico e o partido. */
export function CampaignSection({
  panel,
  party,
  cash,
  nickname,
  onEditTicket,
  onEditPromises,
  onChangeContribution,
  onExpel,
  onLeave,
}: CampaignSectionProps) {
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
      <CampaignActionsCard
        campaign={campaign}
        groups={panel.groups}
        cash={cash}
        party={party}
        parties={partyOrder(panel.parties)}
        poll={panel.polls.at(-1)}
        onHistory={() => history.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
      />
      {panel.electorate.length > 0 && <ElectorateCard panel={panel} party={party} />}
      <div ref={history} className="scroll-mt-4">
        <CampaignHistoryCard campaign={campaign} party={party} nickname={nickname} />
      </div>
      <MyPartyCard
        panel={panel}
        party={party}
        campaign={campaign}
        nickname={nickname}
        onEditTicket={onEditTicket}
        onEditPromises={onEditPromises}
        onChangeContribution={onChangeContribution}
        onExpel={onExpel}
        onLeave={onLeave}
      />
    </div>
  );
}
