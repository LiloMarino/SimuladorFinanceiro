import { MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayList, displayMoneyWhole } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { PARTY_NETWORTH } from "../lib/election-metrics";
import { PartyMark } from "./party-mark";

type RankingCardProps = { panel: ElectionPanel };

/** O patrimônio de cada jogador e o de cada partido (a soma dos filiados). */
export function RankingCard({ panel }: RankingCardProps) {
  const abbrOf = new Map(panel.parties.map((party) => [party.id, party.abbr]));
  const leader = panel.party_standings[0];

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          <h2 className="text-[15px] font-semibold">Ranking da partida</h2>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Individual */}
            <div className="grid content-start">
              <span className="pb-1 text-sm font-medium">Individual</span>
              {panel.player_standings.map((player, index) => (
                <div key={player.nickname} className="flex items-center gap-2.5 py-2 text-[13px]">
                  <span className="w-4.5 font-mono text-muted-foreground">{index + 1}º</span>
                  <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />
                  <span className="min-w-0 flex-1 truncate">
                    {player.nickname}
                    {player.party_id !== null && (
                      <span className="text-xs font-normal text-muted-foreground">
                        {" "}
                        · {abbrOf.get(player.party_id)}
                      </span>
                    )}
                  </span>
                  <span className="font-mono">{displayMoneyWhole(player.total_networth)}</span>
                </div>
              ))}
            </div>

            {/* Partidos */}
            <div className="grid content-start">
              <span className="flex items-center gap-2 pb-1 text-sm font-medium">
                <MetricLabel metric={PARTY_NETWORTH} />
                {panel.decides_match && (
                  <Badge variant="info" size="sm">
                    decide esta partida
                  </Badge>
                )}
              </span>
              {panel.party_standings.length === 0 ? (
                <span className="py-2 text-xs text-muted-foreground">Nenhum jogador filiado ainda.</span>
              ) : (
                panel.party_standings.map((party, index) => (
                  <div key={party.party_id} className="flex items-center gap-2.5 py-2 text-[13px]">
                    <span className="w-4.5 font-mono text-muted-foreground">{index + 1}º</span>
                    <PartyMark abbr={party.abbr} color={party.color} />
                    <span className="min-w-0 flex-1 truncate">
                      {party.name}
                      <span className="text-xs font-normal text-muted-foreground"> · {displayList(party.members)}</span>
                    </span>
                    <span className="font-mono">{displayMoneyWhole(party.total_networth)}</span>
                  </div>
                ))
              )}
            </div>
          </div>
          {leader && (
            <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
              {PARTY_NETWORTH.definition} {PARTY_NETWORTH.example} Hoje o {leader.abbr} lidera com{" "}
              {displayMoneyWhole(leader.total_networth)}.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
