import { MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayList, displayMoneyWhole } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { PARTY_NETWORTH } from "../lib/election-metrics";
import { PartyMark } from "./party-mark";

const ROW = "grid h-11 grid-cols-[2rem_minmax(0,1fr)_auto] items-center gap-2.5 border-b text-[13px]";
const HEADER = "flex items-center gap-2 border-b pb-1.5 text-xs font-medium text-muted-foreground";

type RankingCardProps = { panel: ElectionPanel };

/** O patrimônio de cada jogador e o de cada partido (a soma dos filiados), em colunas de linhas iguais. */
export function RankingCard({ panel }: RankingCardProps) {
  const abbrOf = new Map(panel.parties.map((party) => [party.id, party.abbr]));
  const leader = panel.party_standings[0];

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          <h2 className="text-[15px] font-semibold">Ranking da partida</h2>
          <div className="grid gap-8 md:grid-cols-2">
            {/* Individual */}
            <div className="grid content-start">
              <span className={HEADER}>Individual</span>
              {panel.player_standings.map((player, index) => (
                <div key={player.nickname} className={ROW}>
                  <span className="font-mono text-muted-foreground">{index + 1}º</span>
                  <span className="flex min-w-0 items-center gap-2">
                    <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />
                    <span className="truncate font-medium">{player.nickname}</span>
                    {player.party_id !== null && (
                      <span className="shrink-0 text-[13px] text-muted-foreground">
                        · {abbrOf.get(player.party_id)}
                      </span>
                    )}
                  </span>
                  <span className="font-mono font-semibold">{displayMoneyWhole(player.total_networth)}</span>
                </div>
              ))}
            </div>

            {/* Partidos */}
            <div className="grid content-start">
              <span className={HEADER}>
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
                  <div key={party.party_id} className={ROW}>
                    <span className="font-mono text-muted-foreground">{index + 1}º</span>
                    <span className="flex min-w-0 items-center gap-2">
                      <PartyMark abbr={party.abbr} color={party.color} />
                      <span className="truncate font-medium">{party.name}</span>
                      <span className="min-w-0 truncate text-[13px] text-muted-foreground">
                        · {displayList(party.members)}
                      </span>
                    </span>
                    <span className="font-mono font-semibold">{displayMoneyWhole(party.total_networth)}</span>
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
