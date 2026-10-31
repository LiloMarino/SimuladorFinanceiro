import { Check, Minus } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, RunoffRace, RunoffTransfer } from "@/types";
import { TRUST, UNDECIDED } from "../lib/election-metrics";
import { roundByLargestRemainder, sentTo } from "../lib/runoff";
import { GROUP_INFO } from "../lib/voters";
import { PartyMark } from "./party-mark";
import { GroupIcon } from "./value-chip";
import { partyColor } from "@/shared/lib/party-colors";

type RunoffTransferCardsProps = { panel: ElectionPanel; race: RunoffRace; finalists: ElectionParty[] };

/** Para onde foram os votos de cada partido que ficou de fora, grupo a grupo, e se ele já declarou apoio. */
export function RunoffTransferCards({ panel, race, finalists }: RunoffTransferCardsProps) {
  if (race.transfers.length === 0) return null;
  return (
    <div className="grid gap-4 border-t pt-4">
      {race.transfers.map((transfer) => (
        <TransferCard key={transfer.party_id} panel={panel} race={race} transfer={transfer} finalists={finalists} />
      ))}
    </div>
  );
}

type TransferCardProps = {
  panel: ElectionPanel;
  race: RunoffRace;
  transfer: RunoffTransfer;
  finalists: ElectionParty[];
};

function TransferCard({ panel, race, transfer, finalists }: TransferCardProps) {
  const party = panel.parties.find((candidate) => candidate.id === transfer.party_id);
  const weights = new Map(panel.groups.map((group) => [group.group, group.weight]));
  const declaration = race.declarations.find((item) => item.party_id === transfer.party_id);
  const endorsed = finalists.find((candidate) => candidate.id === transfer.endorsed_party_id);
  if (!party) return null;

  return (
    <div className="grid gap-2.5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-2 text-xs font-medium">
          <PartyMark abbr={party.abbr} color={party.color} size="sm" />
          Estimativa: para onde foram os votos do {party.abbr}
          <span className="font-normal text-muted-foreground">
            · {Number(transfer.voted).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} pontos do eleitorado
          </span>
        </span>
        {transfer.declared ? (
          <Badge variant={endorsed ? "success" : "secondary"} size="sm">
            <Check />
            {endorsed ? `Apoiou o ${endorsed.abbr}` : "Declarou neutralidade"}
            {declaration && ` em ${displayDayMonth(declaration.date)}`}
          </Badge>
        ) : (
          <Badge variant="secondary" size="sm">
            <Minus />
            Ainda não declarou apoio
          </Badge>
        )}
      </div>

      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Grupo</TableHead>
              <TableHead numeric>Votaram no {party.abbr}</TableHead>
              {finalists.map((finalist) => (
                <TableHead key={finalist.id} numeric>
                  <span style={{ color: partyColor(finalist) }}>Foram ao {finalist.abbr}</span>
                </TableHead>
              ))}
              <TableHead numeric>
                <span className="inline-flex items-center gap-1">
                  Indecisos hoje
                  <MetricHint metric={UNDECIDED} />
                </span>
              </TableHead>
              <TableHead numeric>
                <span className="inline-flex items-center gap-1">
                  Confiança no {party.abbr}
                  <MetricHint metric={TRUST} />
                </span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transfer.groups.map((group) => {
              // As partes de cada linha somam o "N de 100" mostrado
              const [undecided, ...sent] = roundByLargestRemainder([
                Number(group.undecided_now),
                ...finalists.map((finalist) => sentTo(group, finalist.id)),
              ]);
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
                  <TableCell numeric>{Math.round(Number(group.voted))} de 100</TableCell>
                  {finalists.map((finalist, index) => (
                    <TableCell key={finalist.id} numeric>
                      {sent[index]}
                    </TableCell>
                  ))}
                  <TableCell numeric>{undecided}</TableCell>
                  <TableCell numeric>{displayPercent(group.trust, 0)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <span className="text-xs text-muted-foreground">
        Leia assim: de cada 100 eleitores do grupo, quantos votaram no {party.abbr} e para onde foram. Os que não foram
        a nenhum dos dois ficam indecisos, e a declaração de apoio, as ações, as contribuições e as doações disputam
        esses votos.
      </span>
    </div>
  );
}
