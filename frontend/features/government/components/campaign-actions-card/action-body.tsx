import { Dices } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { displayDayMonth, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type {
  CampaignAction,
  CampaignActionKind,
  CampaignPanel,
  ElectionParty,
  ElectionPoll,
  VoterGroup,
} from "@/types";
import { nextMonthLabel, targetOf } from "../../lib/campaign";
import { dayAfter } from "../../lib/runoff";
import { PartyMark } from "@/shared/components/party-mark";
import { ActionChoice } from "./action-choice";
import { GroupChoices } from "./group-choices";
import { SummaryBody } from "./summary-body";
import { TvReach } from "./tv-reach";
import { summaryTitle } from "./summary-title";

type ActionBodyProps = {
  campaign: CampaignPanel;
  action: CampaignAction;
  kind: CampaignActionKind;
  onKind: (kind: CampaignActionKind) => void;
  group: VoterGroup;
  onGroup: (group: VoterGroup) => void;
  rival: CampaignPanel["rivals"][number] | undefined;
  rivalId: number | null;
  onRival: (id: number) => void;
  weights: Map<VoterGroup, string>;
  undecided: Map<VoterGroup, string | null> | null;
  cash: number | null;
  party: ElectionParty;
  parties: ElectionParty[];
  poll: ElectionPoll | undefined;
  missing: (action: CampaignAction) => number;
  onRoll: () => void;
};

export function ActionBody({
  campaign,
  action,
  kind,
  onKind,
  group,
  onGroup,
  rival,
  rivalId,
  onRival,
  weights,
  undecided,
  cash,
  party,
  parties,
  poll,
  missing,
  onRoll,
}: ActionBodyProps) {
  const isTv = kind === "TV";
  const isAttack = kind === "ATTACK";
  const target = targetOf(action.targets, isTv ? null : group);
  const price = Number(action.price);
  const short = missing(action);

  const ready = !!target && short === 0 && (!isAttack || rivalId !== null);

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="grid min-w-0 content-start gap-4.5">
        {/* Passo 1: a ação */}
        <div className="grid gap-2">
          <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">1 · Ação</span>
          <div role="radiogroup" aria-label="Ação" className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-4">
            {campaign.actions.map((candidate) => (
              <ActionChoice
                key={candidate.action}
                action={candidate}
                selected={candidate.action === kind}
                short={missing(candidate)}
                cash={cash}
                noRival={candidate.action === "ATTACK" && campaign.rivals.length === 0}
                partyAbbr={campaign.party_abbr}
                onSelect={() => onKind(candidate.action)}
              />
            ))}
          </div>
        </div>

        {/* TV: atinge todos os grupos */}
        {isTv && <TvReach weights={weights} />}

        {/* Passo 2: o grupo */}
        {!isTv && (
          <div className="grid gap-2">
            <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
              <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">2 · Grupo</span>
              <span className="text-xs text-faint-foreground">
                {undecided
                  ? `Repetir a ação no mesmo grupo rende 100%, 50%, 25%, contando desde ${displayDayMonth(dayAfter(campaign.first_round))}; o ganho sai primeiro dos indecisos do grupo`
                  : `Repetir a ação no mesmo grupo no mês rende 100%, 50%, 25%; em ${nextMonthLabel(campaign.today)} volta a 100%`}
              </span>
            </div>
            <GroupChoices
              action={action}
              kind={kind}
              group={group}
              onGroup={onGroup}
              weights={weights}
              undecided={undecided}
              today={campaign.today}
              party={party}
              parties={parties}
              poll={poll}
            />
          </div>
        )}

        {/* Passo 3: o rival, só no ataque */}
        {!isTv && (
          <div className="grid gap-2">
            <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">3 · Rival</span>
            {!isAttack ? (
              <Select disabled value={null} items={{}}>
                <SelectTrigger className="w-70" aria-label="Rival">
                  <SelectValue placeholder="Só no ataque ao rival" />
                </SelectTrigger>
              </Select>
            ) : campaign.rivals.length === 0 ? (
              <span className="text-[13px] text-muted-foreground">
                Sem rival: o {campaign.party_abbr} é o único partido na eleição.
              </span>
            ) : (
              <Select
                value={rivalId === null ? null : String(rivalId)}
                items={Object.fromEntries(
                  campaign.rivals.map((item) => [
                    String(item.party_id),
                    <span key={item.party_id} className="flex items-center gap-2">
                      <PartyMark abbr={item.abbr} color={item.color} size="sm" />
                      {item.name}
                    </span>,
                  ]),
                )}
                onValueChange={(value) => value && onRival(Number(value))}
              >
                <SelectTrigger className="w-70" aria-label="Rival">
                  <SelectValue placeholder="Escolha o rival" />
                </SelectTrigger>
                <SelectContent>
                  {campaign.rivals.map((item) => (
                    <SelectItem key={item.party_id} value={String(item.party_id)}>
                      <PartyMark abbr={item.abbr} color={item.color} size="sm" />
                      {item.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        )}
      </div>

      {/* Resumo do dado */}
      <div className="grid content-start gap-3.5 rounded-[10px] border bg-subtle p-4">
        <div className="grid gap-0.5">
          <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">Resumo</span>
          <b className="text-base">{summaryTitle(kind, group, rival?.abbr ?? null)}</b>
          <span className="text-[12.5px] text-muted-foreground">
            {isTv
              ? "Todos os grupos, pelo peso do eleitorado"
              : isAttack && rival
                ? `${displayPercent(weights.get(group) ?? 0, 0)} do eleitorado · o apoio do ${rival.abbr} fica só com o ${rival.abbr}`
                : `${displayPercent(weights.get(group) ?? 0, 0)} do eleitorado · apoio ${Math.round(Number(target?.support ?? 0))}, rejeição ${Math.round(Number(target?.rejection ?? 0))}`}
          </span>
        </div>

        {target && <SummaryBody campaign={campaign} kind={kind} group={group} target={target} rival={rival?.abbr} />}

        <div className="grid gap-1.5 border-t pt-3">
          <Button size="lg" className="w-full" disabled={!ready} onClick={onRoll}>
            <Dices />
            Rolar o dado · {displayMoney(price)}
          </Button>
          <span className="text-center text-xs text-faint-foreground">
            {short > 0
              ? `Faltam ${displayMoney(short)} no seu caixa`
              : isAttack && rivalId === null
                ? "Escolha o rival para rolar"
                : cash === null
                  ? "Sai da sua carteira"
                  : `Sai da sua carteira: ${displayMoney(cash)} → ${displayMoney(cash - price)}`}
          </span>
        </div>
      </div>
    </div>
  );
}
