import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { CampaignEntry, CampaignPanel, ElectionParty } from "@/types";
import { effectText, entryTitle } from "../lib/campaign";
import { D20 } from "./campaign-dice";
import { PartyMark } from "./party-mark";

type CampaignRecentCardProps = {
  campaign: CampaignPanel;
  party: ElectionParty;
  onHistory: () => void;
};

/** As últimas ações do partido, de quem fez e do que o dado deu. */
export function CampaignRecentCard({ campaign, party, onHistory }: CampaignRecentCardProps) {
  const pricesFrom = campaign.actions.find((action) => action.action === "RALLY");

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <div className="flex items-start justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Últimas ações do {party.abbr}</h2>
              <span className="text-[13px] text-muted-foreground">Só os filiados do {party.abbr} veem</span>
            </div>
            <Button variant="link" size="sm" onClick={onHistory}>
              Histórico ›
            </Button>
          </div>

          {campaign.recent.length === 0 ? (
            <Empty variant="dashed">
              <EmptyHeader>
                <EmptyTitle>Nenhuma ação ainda</EmptyTitle>
                <EmptyDescription>
                  A primeira ação em cada grupo rende 100%.
                  {pricesFrom && ` O comício, a ${displayMoney(pricesFrom.price)}, é o jeito barato de começar.`}
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <div className="grid divide-y">
              {campaign.recent.map((entry) => (
                <RecentRow key={`${entry.kind}-${entry.id}`} entry={entry} party={party} />
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function RecentRow({ entry, party }: { entry: CampaignEntry; party: ElectionParty }) {
  const member = party.members.find((candidate) => candidate.nickname === entry.nickname);
  const received = entry.kind === "ATTACK_RECEIVED";

  return (
    <div className="flex items-center gap-3 py-2 text-[13px]">
      {received ? (
        <PartyMark abbr={entry.party_abbr} color={entry.party_color} size="md" />
      ) : (
        entry.nickname && <PlayerAvatar nickname={entry.nickname} color={member?.color} size="sm" />
      )}
      <div className="grid min-w-0 flex-1 gap-0.5">
        <span className="truncate font-medium">{entryTitle(entry)}</span>
        <span className="text-xs text-muted-foreground">{displayDayMonth(entry.date)}</span>
      </div>
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "font-mono text-xs font-semibold",
            received ? "text-destructive" : entry.kind === "ATTACK" ? "text-muted-foreground" : "text-success",
          )}
        >
          {effectText(entry)}
        </span>
        {entry.roll !== null && entry.band && <D20 value={entry.roll} band={entry.band} size={28} />}
      </div>
    </div>
  );
}
