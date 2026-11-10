import { MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayPoints, POLITICAL_CAPITAL } from "@/shared/lib/political-capital";
import { displayList, displayMoneyWhole, displayNumber } from "@/shared/lib/utils/display";
import type { ElectionPanel, PoliticalCapital } from "@/types";
import { PartyMark } from "@/shared/components/party-mark";

const ROW = "grid h-14 grid-cols-[2rem_minmax(0,1fr)_auto] items-center gap-2.5 border-b text-[13px]";
const HEADER = "flex items-center gap-2 border-b pb-1.5 text-xs font-medium text-muted-foreground";

type RankingCardProps = { panel: ElectionPanel };

/** As parcelas do capital em uma linha; o impeachment aparece só quando tirou pontos. */
function capitalParts(capital: PoliticalCapital) {
  const parts = [
    `Cadeiras ${displayNumber(capital.seats, 0)}`,
    `Presidência ${displayNumber(capital.presidency, 0)}`,
    `Promessas ${displayNumber(capital.promises, 0)}`,
  ];
  if (capital.impeachment !== 0) parts.push(`Impeachment −${displayNumber(Math.abs(capital.impeachment), 0)}`);
  return parts.join(" · ");
}

/** O patrimônio de cada jogador e o capital político de cada partido, em colunas de linhas iguais. */
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
                <MetricLabel metric={POLITICAL_CAPITAL} />
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
                    <span className="grid min-w-0 gap-0.5">
                      <span className="flex min-w-0 items-center gap-2">
                        <PartyMark abbr={party.abbr} color={party.color} />
                        <span className="truncate font-medium">{party.name}</span>
                        <span className="min-w-0 truncate text-[13px] text-muted-foreground">
                          · {displayList(party.members)}
                        </span>
                      </span>
                      <span className="truncate text-xs text-muted-foreground">{capitalParts(party.capital)}</span>
                    </span>
                    <span className="font-mono font-semibold">{displayPoints(party.capital.total)}</span>
                  </div>
                ))
              )}
            </div>
          </div>
          {leader && (
            <p className="rounded-lg bg-subtle px-3 py-2 text-xs leading-normal text-muted-foreground">
              {POLITICAL_CAPITAL.definition}
              {leader.capital.total > 0 && (
                <>
                  {" "}
                  Hoje o {leader.abbr} lidera com {displayPoints(leader.capital.total)}.
                </>
              )}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
