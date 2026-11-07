import { Handshake, LogOut, UserMinus } from "lucide-react";
import { Kpi } from "@/shared/components/kpi";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  displayDayMonth,
  displayMoney,
  displayMoneyWhole,
  displayMonthShort,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { CampaignPanel, ElectionPanel, ElectionParty } from "@/types";
import { BUDGET, SPENT, VOTE_YIELD } from "../lib/election-metrics";
import { signed } from "../lib/campaign";
import { monthYear } from "../lib/election";
import { federationOf, partnerOf } from "../lib/federation";
import { GuidanceRules } from "./guidance-rules";
import { PartyMark } from "@/shared/components/party-mark";
import { PromiseBadges } from "./promise-badges";
import { ValueChips } from "@/shared/components/value-chip";

type MyPartyCardProps = {
  panel: ElectionPanel;
  party: ElectionParty;
  /** A campanha traz a última cobrança da verba de base */
  campaign: CampaignPanel;
  nickname: string;
  onEditTicket: () => void;
  onEditPromises: () => void;
  onChangeContribution: () => void;
  onExpel: (nickname: string) => void;
  onLeave: () => void;
  onProposeFederation: () => void;
  onLeaveFederation: () => void;
};

function roleOf(member: ElectionParty["members"][number]) {
  const roles = [];
  if (member.is_founder) roles.push("Fundador");
  if (member.is_candidate) roles.push("candidato");
  if (member.vice === "ACCEPTED") roles.push("vice na chapa");
  if (member.vice === "PENDING") roles.push("indicado para vice · convite pendente");
  return roles.length > 0 ? roles.join(" · ") : "Filiado";
}

/** O partido de quem vê em três colunas: verba e filiados, promessas e bandeiras, orientação da bancada. */
export function MyPartyCard({
  panel,
  party,
  campaign,
  nickname,
  onEditTicket,
  onEditPromises,
  onChangeContribution,
  onExpel,
  onLeave,
  onProposeFederation,
  onLeaveFederation,
}: MyPartyCardProps) {
  const mine = panel.my_party;
  const federation = federationOf(panel.federations, party.id);
  const partner = federation && panel.parties.find((candidate) => candidate.id === partnerOf(federation, party.id));
  const locked = panel.phase === "BETWEEN_ROUNDS";

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          {/* Cabeçalho */}
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <PartyMark abbr={party.abbr} color={party.color} size="lg" />
              <span className="grid gap-0.5">
                <span className="text-xs font-medium text-muted-foreground">Seu partido</span>
                <b className="text-base">{party.name}</b>
                <span className="text-xs text-muted-foreground">
                  {mine?.is_founder ? "Você fundou o partido" : `Fundado por ${party.founder}`} · em{" "}
                  {displayMonthShort(party.founded)} {party.founded.slice(0, 4)}
                  {mine?.seats === 0 && ` · Sem cadeira até a eleição de ${monthYear(panel.dates.first_round)}`}
                </span>
              </span>
            </div>
            {panel.can_edit_ticket && (
              <Button size="sm" variant="outline" onClick={onEditTicket}>
                Montar a chapa
              </Button>
            )}
          </div>

          <div className="grid items-start gap-8 border-t pt-4 lg:grid-cols-3">
            {/* Verba e filiados */}
            <div className="grid content-start gap-3">
              <div className="grid grid-cols-2 gap-3">
                <Kpi
                  label={
                    <>
                      {BUDGET.label}
                      <MetricHint metric={BUDGET} />
                    </>
                  }
                  value={displayMoneyWhole(party.budget)}
                />
                <Kpi
                  label={
                    <>
                      {SPENT.label}
                      <MetricHint metric={SPENT} />
                    </>
                  }
                  value={displayMoneyWhole(party.spent)}
                />
              </div>

              {/* Verba de base */}
              <div className="grid">
                <div className="flex items-baseline justify-between gap-3 pb-1.5">
                  <span className="text-sm font-medium">Verba de base</span>
                  <span className="text-xs text-muted-foreground">
                    A contribuição dos filiados, cobrada todo dia 1º
                  </span>
                </div>
                {party.members.map((member) => {
                  const isMe = member.nickname === nickname;
                  return (
                    <div
                      key={member.nickname}
                      className="grid grid-cols-[28px_1fr_auto_auto] items-center gap-2.5 border-t py-2 text-[13px]"
                    >
                      <PlayerAvatar nickname={member.nickname} color={member.color} />
                      <span className="grid gap-px">
                        <b className="font-medium">
                          {member.nickname}
                          {isMe && " (você)"}
                        </b>
                        <span className="text-xs text-muted-foreground">{roleOf(member)}</span>
                      </span>
                      <span className="font-mono font-semibold">{displayMoney(member.contribution)}/mês</span>
                      {isMe ? (
                        <Button size="xs" variant="outline" disabled={locked} onClick={onChangeContribution}>
                          Mudar
                        </Button>
                      ) : mine?.is_founder ? (
                        <Button
                          size="xs"
                          variant="outline-destructive"
                          disabled={locked}
                          onClick={() => onExpel(member.nickname)}
                        >
                          <UserMinus />
                          Expulsar
                        </Button>
                      ) : (
                        <span />
                      )}
                    </div>
                  );
                })}
              </div>
              {campaign.last_charge_date && campaign.last_charge_amount && campaign.last_charge_points && (
                <div className="flex items-baseline justify-between gap-3 border-t pt-2.5">
                  <span className="text-xs font-medium text-muted-foreground">
                    Em {displayDayMonth(campaign.last_charge_date)}, {displayMoney(campaign.last_charge_amount)} viraram
                  </span>
                  <span className="font-mono text-[13px] font-semibold text-success">
                    {signed(campaign.last_charge_points, 1)} em cada grupo
                  </span>
                </div>
              )}

              {/* Quanto a verba rende */}
              <div className="grid gap-1.5">
                <span className="text-sm font-medium">
                  <MetricLabel metric={VOTE_YIELD} />
                </span>
                <span className="text-xs text-muted-foreground">{VOTE_YIELD.description}.</span>
              </div>
            </div>

            {/* Promessas e bandeiras */}
            <div className="grid content-start gap-5">
              <div className="grid gap-1.5">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-medium">Promessas da chapa</span>
                  {mine?.is_founder && (
                    <Button size="xs" variant="outline" onClick={onEditPromises}>
                      {party.promises.length > 0 ? "Editar promessas" : "Escolher promessas"}
                    </Button>
                  )}
                </div>
                {party.promises.length > 0 ? (
                  <PromiseBadges promises={party.promises} />
                ) : (
                  <span className="text-xs text-muted-foreground">A chapa ainda não prometeu nada.</span>
                )}
              </div>

              <div className="grid gap-1.5">
                <span className="text-sm font-medium">Bandeiras</span>
                <ValueChips values={party.flags} />
              </div>
            </div>

            {/* Orientação da bancada */}
            <div className="grid content-start gap-4">
              {mine && <GuidanceRules rules={mine.guidance} isLeader={mine.is_founder} abbr={party.abbr} />}
              {/* Federação */}
              {(federation || mine?.is_founder) && (
                <div className="grid gap-1.5">
                  <span className="text-sm font-medium">Federação</span>
                  {federation ? (
                    <>
                      <span className="text-xs text-muted-foreground">
                        {federation.name}, com o {partner?.abbr}, até {displayShortDate(federation.ends_on)}.
                      </span>
                      {panel.can_federate && (
                        <Button
                          variant="outline-destructive"
                          size="sm"
                          className="justify-self-start"
                          onClick={onLeaveFederation}
                        >
                          Sair da federação
                        </Button>
                      )}
                    </>
                  ) : (
                    <>
                      <span className="text-xs text-muted-foreground">
                        {panel.federation_block ??
                          "Dois partidos viram uma lista só no Congresso e somam os votos na barreira."}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        className="justify-self-start"
                        disabled={!panel.can_federate || panel.federation_block !== null}
                        onClick={onProposeFederation}
                      >
                        <Handshake />
                        Propor federação
                      </Button>
                    </>
                  )}
                </div>
              )}
              <Button
                variant="outline-destructive"
                size="sm"
                className="justify-self-start"
                disabled={locked}
                onClick={onLeave}
              >
                <LogOut />
                Sair do partido
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
