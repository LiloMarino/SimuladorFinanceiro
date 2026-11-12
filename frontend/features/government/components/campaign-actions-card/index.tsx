import { useRef, useState } from "react";
import { Lock, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import type {
  CampaignAction,
  CampaignActionKind,
  CampaignPanel,
  CampaignTarget,
  ElectionParty,
  ElectionPoll,
  VoterGroup,
  VoterGroupInfo,
} from "@/types";
import { bandEffect, monthLabel, ratePercent, targetOf } from "../../lib/campaign";
import { CampaignRollDialog } from "../campaign-roll-dialog";
import { ActionBody } from "./action-body";
import { summaryTitle } from "./summary-title";

type CampaignActionsCardProps = {
  campaign: CampaignPanel;
  /** Os grupos de eleitores, para o peso de cada um */
  groups: VoterGroupInfo[];
  /** O partido de quem vê e os da corrida: a pesquisa no grupo compara o primeiro com o líder */
  party: ElectionParty;
  parties: ElectionParty[];
  /** A pesquisa mais recente, ainda ausente antes da primeira */
  poll: ElectionPoll | undefined;
  onHistory: () => void;
};

/** As quatro ações avulsas de campanha em passos (ação, grupo, rival), com o resumo do dado sempre à vista. */
export function CampaignActionsCard({ campaign, groups, party, parties, poll, onHistory }: CampaignActionsCardProps) {
  const [kind, setKind] = useState<CampaignActionKind>("EVENT");
  const [group, setGroup] = useState<VoterGroup>("RETIREES");
  const [chosenRival, setChosenRival] = useState<number | null>(null);
  const [rolling, setRolling] = useState(false);
  const top = useRef<HTMLDivElement>(null);

  const weights = new Map(groups.map((info) => [info.group, info.weight]));
  // No 2º turno cada grupo mostra os indecisos que as ações disputam
  const undecided = campaign.groups.some((item) => item.undecided !== null)
    ? new Map(campaign.groups.map((item) => [item.group, item.undecided]))
    : null;
  const action = campaign.actions.find((candidate) => candidate.action === kind);
  const rivalId = chosenRival ?? (campaign.rivals.length === 1 ? (campaign.rivals[0]?.party_id ?? null) : null);
  const rival = campaign.rivals.find((candidate) => candidate.party_id === rivalId);
  const cash = Number(campaign.cash);

  /** O que falta no caixa do partido para pagar a ação */
  const missing = (candidate: CampaignAction) => Math.max(0, Number(candidate.price) - cash);

  return (
    <Card>
      <CardContent>
        <div ref={top} className="grid scroll-mt-4 gap-4">
          {/* Cabeçalho */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Ações de campanha</h2>
              <span className="text-[13px] text-muted-foreground">
                Qualquer filiado faz e a ação sai do caixa do partido. O resultado sai de um dado e só o{" "}
                {campaign.party_abbr} vê.
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="secondary">
                <Lock />
                Só o {campaign.party_abbr} vê
              </Badge>
              <Button variant="link" size="sm" onClick={onHistory}>
                Histórico ›
              </Button>
            </div>
          </div>

          {!campaign.open || !action ? (
            <Alert variant="muted">
              <Info />
              <AlertTitle>As ações fecharam</AlertTitle>
              <AlertDescription>{campaign.closed_reason}</AlertDescription>
            </Alert>
          ) : (
            <ActionBody
              campaign={campaign}
              action={action}
              kind={kind}
              onKind={setKind}
              group={group}
              onGroup={setGroup}
              rival={rival}
              rivalId={rivalId}
              onRival={setChosenRival}
              weights={weights}
              undecided={undecided}
              cash={cash}
              party={party}
              parties={parties}
              poll={poll}
              missing={missing}
              onRoll={() => setRolling(true)}
            />
          )}
        </div>
      </CardContent>

      {rolling && action && (
        <CampaignRollDialog
          action={action}
          target={targetOf(action.targets, kind === "TV" ? null : group) ?? action.targets[0]!}
          request={{ action: kind, group: kind === "TV" ? null : group, rival_id: kind === "ATTACK" ? rivalId : null }}
          title={summaryTitle(kind, group, rival?.abbr ?? null)}
          subtitle={rollSubtitle(campaign, action, targetOf(action.targets, kind === "TV" ? null : group))}
          partyAbbr={campaign.party_abbr}
          rivalAbbr={rival?.abbr ?? null}
          onClose={() => setRolling(false)}
          onAnother={() => {
            setRolling(false);
            top.current?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
        />
      )}
    </Card>
  );
}

/** "2ª vez em ago · rende 50% · ganho normal +3": o que a pessoa lê antes de pagar o dado. */
function rollSubtitle(campaign: CampaignPanel, action: CampaignAction, target: CampaignTarget | undefined) {
  if (!target) return "";
  const normal = target.bands.find((band) => band.band === "NORMAL");
  const parts = [
    `${target.uses_this_month + 1}ª vez em ${monthLabel(campaign.today)}`,
    `rende ${ratePercent(target.rate)}`,
  ];
  if (normal) parts.push(`ganho normal ${bandEffect(normal)}`);
  return parts.join(" · ") + (action.advantage ? " · dois dados" : "");
}
