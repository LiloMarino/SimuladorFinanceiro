import { MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { BUDGET, INTENTION, SPENT } from "../lib/election-metrics";
import { PersonMark, PartyMark } from "./party-mark";
import { ValueChips } from "./value-chip";

const pointsFormat = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });

type PartiesCardProps = { panel: ElectionPanel };

/** Todos os partidos da disputa: chapa, filiados, intenção, verba, gasto e bandeiras. Tudo é público. */
export function PartiesCard({ panel }: PartiesCardProps) {
  const mineId = panel.my_party?.party_id;
  const ticketOpen = panel.phase === "CAMPAIGN" && panel.today <= panel.dates.ticket_deadline;
  const sorted = [...panel.parties].sort(
    (a, b) => Number(b.intention_points) - Number(a.intention_points) || a.id - b.id,
  );

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          <div className="grid gap-0.5">
            <h2 className="text-[15px] font-semibold">Partidos</h2>
            <span className="text-xs text-muted-foreground">
              Filiados, contribuições, verba, gasto e bandeiras de cada partido são públicos, como a prestação de contas
              de uma campanha.
            </span>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Partido e chapa</TableHead>
                <TableHead>Filiados</TableHead>
                <TableHead numeric>
                  <MetricLabel metric={INTENTION} />
                </TableHead>
                <TableHead numeric>
                  <MetricLabel metric={BUDGET} />
                </TableHead>
                <TableHead numeric>
                  <MetricLabel metric={SPENT} />
                </TableHead>
                <TableHead>Bandeiras</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sorted.map((party) => (
                <PartyRow key={party.id} party={party} current={party.id === mineId} ticketOpen={ticketOpen} />
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function ticketLine(party: ElectionParty, ticketOpen: boolean) {
  if (party.vice) {
    return party.vice_phase === "PENDING" ? `vice: ${party.vice.name}, aguardando` : `vice: ${party.vice.name}`;
  }
  // Com a inscrição aberta a chapa ainda pode ganhar vice; fechada, concorre sem
  return ticketOpen && !party.is_computer ? "vice: vaga aberta" : "sem vice";
}

function PartyRow({ party, current, ticketOpen }: { party: ElectionParty; current: boolean; ticketOpen: boolean }) {
  return (
    <TableRow variant={current ? "current" : "default"}>
      <TableCell>
        <span className="grid gap-1">
          <span className="flex items-center gap-2">
            <PartyMark abbr={party.abbr} color={party.color} />
            <b className="font-medium">{party.name}</b>
          </span>
          <span className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
            {party.candidate ? (
              <>
                <PersonMark person={party.candidate} />
                {party.candidate.name}
                <span>·</span>
                {ticketLine(party, ticketOpen)}
              </>
            ) : (
              "sem candidato elegível"
            )}
            {!party.ticket_chosen && !party.is_computer && (
              <Badge variant="secondary" size="sm">
                chapa padrão
              </Badge>
            )}
          </span>
        </span>
      </TableCell>
      <TableCell>
        {party.is_computer ? (
          <Badge variant="secondary" size="sm">
            computador
          </Badge>
        ) : (
          <span className="inline-flex">
            {party.members.map((member, index) => (
              <span key={member.nickname} className={index > 0 ? "-ml-1.5" : undefined} title={member.nickname}>
                <PlayerAvatar nickname={member.nickname} color={member.color} size="sm" />
              </span>
            ))}
          </span>
        )}
      </TableCell>
      <TableCell numeric className="whitespace-nowrap">
        {pointsFormat.format(Number(party.intention_points))}%
      </TableCell>
      <TableCell numeric>{displayMoneyWhole(party.budget)}</TableCell>
      <TableCell numeric>{displayMoneyWhole(party.spent)}</TableCell>
      <TableCell>
        <ValueChips values={party.flags} />
      </TableCell>
    </TableRow>
  );
}
