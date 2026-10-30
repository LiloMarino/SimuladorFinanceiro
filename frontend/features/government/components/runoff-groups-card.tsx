import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionRound } from "@/types";
import { NOT_VOTED } from "../lib/election-metrics";
import { GROUP_INFO, partyFill, pollPoints } from "../lib/voters";
import { GroupIcon } from "./value-chip";

type RunoffGroupsCardProps = { panel: ElectionPanel; result: ElectionRound };

/** O 2º turno por grupo de eleitores, depois da votação: de cada 100 eleitores do grupo, quantos foram a cada finalista e quantos não votaram. */
export function RunoffGroupsCard({ panel, result }: RunoffGroupsCardProps) {
  const finalists = result.parties
    .filter((party) => result.finalists.includes(party.party_id))
    .sort((a, b) => Number(b.share) - Number(a.share) || a.party_id - b.party_id);
  const weights = new Map(panel.groups.map((group) => [group.group, group.weight]));
  const winnerOf = (points: Map<number, number>) =>
    finalists.reduce((best, party) =>
      (points.get(party.party_id) ?? 0) > (points.get(best.party_id) ?? 0) ? party : best,
    );
  const leastVoting = [...result.groups]
    .sort((a, b) => Number(b.undecided) - Number(a.undecided))
    .slice(0, 2)
    .map((group) => GROUP_INFO[group.group].label);
  const total = new Map(finalists.map((party) => [party.party_id, Number(party.points)]));
  const winner = finalists.find((party) => party.party_id === result.winner);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-0.5">
            <h2 className="text-[15px] font-semibold">O 2º turno por grupo</h2>
            <span className="text-[13px] text-muted-foreground">
              De cada 100 eleitores do grupo. Resultado oficial, exato e público.
            </span>
          </div>
          <div className="overflow-hidden rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Grupo</TableHead>
                  {finalists.map((party) => (
                    <TableHead key={party.party_id} numeric>
                      <span style={{ color: partyFill(party) }}>{party.abbr}</span>
                    </TableHead>
                  ))}
                  <TableHead numeric>
                    <span className="inline-flex items-center gap-1">
                      Não votaram
                      <MetricHint metric={NOT_VOTED} />
                    </span>
                  </TableHead>
                  <TableHead>Venceu</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.groups.map((group) => {
                  const points = pollPoints(group.entries);
                  const leader = winnerOf(points);
                  return (
                    <TableRow key={group.group}>
                      <TableCell>
                        <span className="flex items-center gap-2.5">
                          <GroupIcon group={group.group} className="size-7" />
                          <span className="grid gap-px">
                            <b className="text-[13px] font-semibold">{GROUP_INFO[group.group].label}</b>
                            <span className="text-xs text-muted-foreground">
                              {displayPercent(weights.get(group.group) ?? 0, 0)} do eleitorado
                            </span>
                          </span>
                        </span>
                      </TableCell>
                      {finalists.map((party) => (
                        <TableCell key={party.party_id} numeric>
                          {Math.round(points.get(party.party_id) ?? 0)}
                        </TableCell>
                      ))}
                      <TableCell numeric>{Math.round(Number(group.undecided))}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" size="sm">
                          <span style={{ color: partyFill(leader) }}>{leader.abbr}</span>
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })}
                <TableRow>
                  <TableCell>
                    <b className="text-[13px] font-semibold">Eleitorado</b>
                  </TableCell>
                  {finalists.map((party) => (
                    <TableCell key={party.party_id} numeric>
                      {displayNumber(total.get(party.party_id) ?? 0, 1)}
                    </TableCell>
                  ))}
                  <TableCell numeric>{displayNumber(result.not_voted, 1)}</TableCell>
                  <TableCell>
                    {winner && (
                      <Badge variant="success" size="sm">
                        {winner.abbr}
                      </Badge>
                    )}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
          {leastVoting.length > 0 && (
            <span className="text-xs text-muted-foreground">{leastVoting.join(" e ")} foram os que menos votaram.</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
