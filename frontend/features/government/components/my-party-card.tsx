import { LogOut, UserMinus } from "lucide-react";
import { Kpi } from "@/shared/components/kpi";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayMoney, displayMoneyWhole, displayMonthShort } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { BUDGET, SPENT, VOTE_YIELD } from "../lib/election-metrics";
import { monthlyYield } from "../lib/election";
import { PartyMark } from "./party-mark";
import { ValueChips } from "./value-chip";
import { YieldChart } from "./yield-chart";

type MyPartyCardProps = {
  panel: ElectionPanel;
  party: ElectionParty;
  nickname: string;
  onEditTicket: () => void;
  onChangeContribution: () => void;
  onExpel: (nickname: string) => void;
  onLeave: () => void;
};

const yieldLabel = (amount: number) =>
  monthlyYield(amount).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

function roleOf(member: ElectionParty["members"][number]) {
  const roles = [];
  if (member.is_founder) roles.push("Fundador");
  if (member.is_candidate) roles.push("candidato");
  if (member.vice === "ACCEPTED") roles.push("vice na chapa");
  if (member.vice === "PENDING") roles.push("indicado para vice · convite pendente");
  return roles.length > 0 ? roles.join(" · ") : "Filiado";
}

/** O partido de quem vê: verba, filiados e contribuições, a curva de rendimento e a promessa. */
export function MyPartyCard({
  panel,
  party,
  nickname,
  onEditTicket,
  onChangeContribution,
  onExpel,
  onLeave,
}: MyPartyCardProps) {
  const mine = panel.my_party;
  const locked = panel.phase === "BETWEEN_ROUNDS";
  const budget = Number(party.budget);
  const doubled = budget * 2;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-[15px] font-semibold">Seu partido</h2>
            {panel.can_edit_ticket && (
              <Button size="sm" variant="outline" onClick={onEditTicket}>
                Montar a chapa
              </Button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <PartyMark abbr={party.abbr} color={party.color} size="lg" />
            <span className="grid gap-0.5">
              <b className="text-[15px]">{party.name}</b>
              <span className="text-xs text-muted-foreground">
                {mine?.is_founder ? "Você fundou o partido" : `Fundado por ${party.founder}`} · em{" "}
                {displayMonthShort(party.founded)} {party.founded.slice(0, 4)}
              </span>
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Kpi
              label={
                <>
                  {BUDGET.label}
                  <MetricHint metric={BUDGET} />
                </>
              }
              value={displayMoneyWhole(party.budget)}
              note="Por mês: a soma das contribuições dos filiados."
            />
            <Kpi
              label={
                <>
                  {SPENT.label}
                  <MetricHint metric={SPENT} />
                </>
              }
              value={displayMoneyWhole(party.spent)}
              note="Cada parte já saiu do patrimônio de quem contribuiu."
            />
          </div>

          {/* Filiados */}
          <div className="grid">
            <div className="flex justify-between pb-1.5 text-xs text-muted-foreground">
              <span>Filiados</span>
              <span>Contribuição mensal</span>
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
                  <span className="font-mono font-semibold">{displayMoney(member.contribution)}</span>
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
          <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
            Cada filiado escolhe quanto contribui, e pode ser zero.
            {mine?.is_founder &&
              " Como quem fundou o partido, você escolhe o candidato entre os filiados, o vice entre os jogadores da sala e pode expulsar."}
          </p>

          {/* Quanto a verba rende */}
          <div className="grid gap-1.5">
            <span className="text-sm font-medium">
              <MetricLabel metric={VOTE_YIELD} />
            </span>
            <YieldChart budget={budget} color={party.color} />
            <span className="text-xs text-muted-foreground">
              {VOTE_YIELD.description}.
              {budget > 0
                ? ` Com ${displayMoneyWhole(budget)} o ${party.abbr} ganha +${yieldLabel(budget)}; dobrar para ${displayMoneyWhole(doubled)} dá +${yieldLabel(doubled)}, e não +${(monthlyYield(budget) * 2).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}.`
                : " Sem verba, o partido não ganha pontos."}
            </span>
          </div>

          {/* Bandeiras */}
          <div className="grid gap-1.5">
            <span className="text-sm font-medium">Bandeiras</span>
            <ValueChips values={party.flags} />
            <span className="text-xs text-muted-foreground">
              Elas ficam para sempre; o perfil do partido parte delas e se move com as medidas que ele aprova no
              governo.
            </span>
          </div>

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
      </CardContent>
    </Card>
  );
}
