import { useState } from "react";
import { PartyMark } from "@/shared/components/party-mark";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import type { ElectionMap, MapParty } from "@/types";
import {
  classifyPlace,
  formatPercent,
  partyOf,
  placesOf,
  pointsOf,
  standings,
  type MapDivision,
} from "../lib/map-lenses";

type MapPlacesTableProps = {
  map: ElectionMap;
  division: MapDivision;
  /** O partido da última coluna. */
  party: MapParty | undefined;
  selected: string;
  onSelect: (code: string) => void;
  /** Com a lente Resultado a tabela mostra a apuração; nas demais, a pesquisa. */
  showResult: boolean;
};

const COLLAPSED_ROWS = 7;

/** Os lugares do maior eleitorado ao menor: quem lidera, por quanto e o desempenho do partido escolhido. */
export function MapPlacesTable({ map, division, party, selected, onSelect, showResult }: MapPlacesTableProps) {
  const [expanded, setExpanded] = useState(false);
  const source: "poll" | "result" | null = map.poll && !showResult ? "poll" : map.result ? "result" : null;
  const all = [...placesOf(map, division)].sort((a, b) => b.electorate - a.electorate);
  const shown = expanded ? all : all.slice(0, COLLAPSED_ROWS);
  const unit = division === "state" ? "Estados" : "Regiões";

  return (
    <Card id="map-table">
      <CardContent>
        <div className="grid gap-3">
          <b className="text-[15px]">{unit}, do maior para o menor</b>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{division === "state" ? "Estado" : "Região"}</TableHead>
                <TableHead>Lidera</TableHead>
                <TableHead className="text-right">Dif.</TableHead>
                <TableHead className="text-right">{party?.abbr ?? ""}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {shown.map((place) => {
                const ranked = source ? standings(map, place.code, source) : [];
                const verdict = classifyPlace(ranked, source === "poll" ? place.margin : 0);
                const leader = verdict?.kind === "leads" ? partyOf(map, verdict.leader) : undefined;
                const total = ranked.reduce((sum, row) => sum + row.points, 0);
                const own = party ? pointsOf(ranked, party.id) : 0;
                const ownValue = source === "result" ? (total > 0 ? (own / total) * 100 : 0) : own;
                return (
                  <TableRow key={place.code} variant={place.code === selected ? "current" : "default"}>
                    <TableCell>
                      <button
                        type="button"
                        className="flex items-center gap-2 text-left text-[13px] font-medium"
                        aria-pressed={place.code === selected}
                        onClick={() => onSelect(place.code)}
                      >
                        {division === "state" ? place.code : place.name}
                        <span className="text-xs font-normal text-muted-foreground">
                          {formatPercent(Number(place.electorate_share) * 100, 1)}
                        </span>
                      </button>
                    </TableCell>
                    <TableCell>
                      {leader ? (
                        <PartyMark abbr={leader.abbr} color={leader.color} size="sm" />
                      ) : verdict ? (
                        <Badge variant="warning">Empate</Badge>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                    <TableCell numeric>
                      {verdict ? verdict.lead.toLocaleString("pt-BR", { maximumFractionDigits: 1 }) : "—"}
                    </TableCell>
                    <TableCell numeric>{source ? formatPercent(ownValue, source === "poll" ? 0 : 1) : "—"}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          {all.length > COLLAPSED_ROWS && (
            <Button
              variant="link"
              size="sm"
              className="justify-self-start"
              onClick={() => setExpanded((open) => !open)}
            >
              {expanded ? "Ver menos" : `Ver os ${all.length}`}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
