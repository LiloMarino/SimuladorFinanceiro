import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayList, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, RunoffRace } from "@/types";
import { PartyMark, PersonMark } from "./party-mark";
import { RunoffTransferCards } from "./runoff-transfer-cards";
import { partyColor } from "@/shared/lib/party-colors";

type FirstRoundCardProps = { panel: ElectionPanel; race: RunoffRace; finalists: ElectionParty[] };

/** O resultado do 1º turno na página, com a transferência dos votos de quem ficou de fora logo abaixo. */
export function FirstRoundCard({ panel, race, finalists }: FirstRoundCardProps) {
  const result = panel.last_result?.round === 1 ? panel.last_result : undefined;
  if (!result) return null;
  const ranked = [...result.parties].sort((a, b) => Number(b.share) - Number(a.share) || a.party_id - b.party_id);
  const eliminated = ranked.filter((party) => !result.finalists.includes(party.party_id));

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4.5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-0.5">
              <h2 className="text-[15px] font-semibold">Resultado do 1º turno</h2>
              <span className="max-w-3xl text-[13px] text-muted-foreground">
                {displayShortDate(result.date)} · votos válidos, exatos.
                {eliminated.length > 0 &&
                  ` Abaixo, para onde foram os votos do ${displayList(eliminated.map((party) => party.abbr))}: cada grupo divide esses votos pela afinidade com os finalistas, e quem não gosta de nenhum dos dois fica indeciso.`}
              </span>
            </div>
            <Badge variant="info">Pública · com margem</Badge>
          </div>

          <div className="grid gap-2.5">
            {ranked.map((party) => {
              const runs = result.finalists.includes(party.party_id);
              return (
                <div
                  key={party.party_id}
                  className="grid grid-cols-[minmax(0,220px)_64px_1fr_auto] items-center gap-3 text-[13px]"
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                    {party.candidate && <PersonMark person={party.candidate} />}
                    <span className="truncate">{party.candidate?.name ?? party.name}</span>
                  </span>
                  <span className="font-mono text-[15px] font-semibold">{displayPercent(party.share, 1)}</span>
                  <span className="relative h-2.5 rounded-xs bg-muted">
                    <span
                      className="absolute inset-y-0 left-0 rounded-xs opacity-85"
                      style={{ width: `${Number(party.share) * 100}%`, backgroundColor: partyColor(party) }}
                    />
                  </span>
                  <Badge variant={runs ? "success" : "secondary"} size="sm">
                    {runs ? "Vai ao 2º turno" : "Fora do 2º turno"}
                  </Badge>
                </div>
              );
            })}
          </div>

          <RunoffTransferCards panel={panel} race={race} finalists={finalists} />
        </div>
      </CardContent>
    </Card>
  );
}
