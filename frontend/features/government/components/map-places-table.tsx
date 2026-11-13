import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardTitle } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { NO_COLOR, partyColor } from "@/shared/lib/party-colors";
import { displayPercent } from "@/shared/lib/utils/display";
import type { ElectionMap, MapPlace } from "@/types";
import {
  dayMonth,
  duelOf,
  formatPercent,
  momentSource,
  partyOf,
  placeByCode,
  placesOf,
  standings,
  type MapDivision,
  type MomentSource,
} from "../lib/map-lenses";

type MapPlacesTableProps = {
  map: ElectionMap;
  division: MapDivision;
  selected: string;
  onSelect: (code: string) => void;
};

const COLLAPSED_ROWS = 7;

const MILLIONS = { minimumFractionDigits: 1, maximumFractionDigits: 1 } as const;

type PartyShareProps = { map: ElectionMap; partyId: number; value: number; digits: number };

// A sigla do partido na cor dele, com o percentual do lugar
function PartyShare({ map, partyId, value, digits }: PartyShareProps) {
  const party = partyOf(map, partyId);
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap">
      <span
        aria-hidden
        className="size-2.5 rounded-[3px]"
        style={{ background: party ? partyColor(party) : NO_COLOR }}
      />
      <b className="font-semibold">{party?.abbr ?? "—"}</b>
      <span className="font-mono text-muted-foreground tabular-nums">{formatPercent(value, digits)}</span>
    </span>
  );
}

/** Frase de apoio do cabeçalho: como ler a Dif. (com um lugar da própria lista como exemplo) e o empate. */
function legend(map: ElectionMap, places: MapPlace[], source: MomentSource, division: MapDivision) {
  const example = places
    .map((place) => ({ place, duel: duelOf(standings(map, place.code, source), source, place.margin) }))
    .find((item) => item.duel?.second);
  const duel = example?.duel;
  const second = duel?.second;
  if (!example || !duel || !second) return "Dif.: distância em pontos percentuais (p.p.) entre o 1º e o 2º.";
  const digits = source === "poll" ? 0 : 1;
  const label = division === "state" ? example.place.code : example.place.name;
  const sample = `${label}, ${formatPercent(duel.first.value, digits)} − ${formatPercent(second.value, digits)} = ${duel.gap.toLocaleString("pt-BR", { maximumFractionDigits: digits })} p.p.`;
  const ties =
    source === "poll"
      ? ` Empate: a diferença cabe na margem de erro ${division === "state" ? "do estado" : "da região"} (em ${label}, ±${example.place.margin} p.p.).`
      : "";
  return `Dif.: distância em pontos percentuais (p.p.) entre o 1º e o 2º; em ${sample}${ties}`;
}

/** Os lugares do maior eleitorado ao menor: tamanho, quem ficou em 1º e 2º e a distância entre eles. */
export function MapPlacesTable({ map, division, selected, onSelect }: MapPlacesTableProps) {
  const [expanded, setExpanded] = useState(false);
  const source = momentSource(map);
  const all = [...placesOf(map, division)].sort((a, b) => b.electorate - a.electorate);
  const shown = expanded ? all : all.slice(0, COLLAPSED_ROWS);
  const unit = division === "state" ? "Estados" : "Regiões";
  const noun = division === "state" ? "estado" : "região";
  const biggest = all[0]?.electorate ?? 1;
  const digits = source === "poll" ? 0 : 1;

  return (
    <Card size="flush">
      {/* Cabeçalho */}
      <div className="flex items-end justify-between gap-6 px-5 pt-4 pb-3">
        <div className="grid gap-0.5">
          <CardTitle>{unit}, do maior para o menor</CardTitle>
          <span className="text-xs text-muted-foreground">
            {source
              ? legend(map, all, source, division)
              : `As pesquisas por ${noun} começam em ${dayMonth(map.opens_on)} ${map.opens_on.slice(0, 4)}. Até lá, a lente Onde vive cada grupo mostra o eleitorado.`}
          </span>
        </div>
        <span className="text-xs whitespace-nowrap text-sidebar-muted">
          {all.length} {division === "state" ? "estados" : "regiões"} · ordem pelo eleitorado
        </span>
      </div>

      {/* Listagem */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{division === "state" ? "Estado" : "Região"}</TableHead>
            {division === "state" && <TableHead>Região</TableHead>}
            <TableHead>Eleitorado</TableHead>
            <TableHead>1º</TableHead>
            <TableHead>2º</TableHead>
            <TableHead numeric>Dif.</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {shown.map((place) => {
            const duel = source ? duelOf(standings(map, place.code, source), source, place.margin) : null;
            const region = place.region ? placeByCode(map, place.region) : undefined;
            return (
              <TableRow
                key={place.code}
                variant={place.code === selected ? "current" : "default"}
                onActivate={() => onSelect(place.code)}
              >
                <TableCell className="whitespace-nowrap">
                  {division === "state" ? (
                    <>
                      <b>{place.code}</b> <span className="text-muted-foreground">{place.name}</span>
                    </>
                  ) : (
                    <b>{place.name}</b>
                  )}
                </TableCell>
                {division === "state" && (
                  <TableCell variant="note" className="whitespace-nowrap">
                    {region?.name ?? "—"}
                  </TableCell>
                )}
                <TableCell>
                  <span className="inline-flex items-center gap-2 whitespace-nowrap">
                    <span className="font-mono tabular-nums">
                      {(place.electorate / 1_000_000).toLocaleString("pt-BR", MILLIONS)} mi
                    </span>
                    <Progress
                      size="sm"
                      className="w-16 flex-nowrap"
                      value={(place.electorate / biggest) * 100}
                      color="var(--sidebar-muted)"
                      aria-label={`Eleitorado ${displayPercent(place.electorate_share, 1)} do país`}
                    />
                    <span className="font-mono text-xs text-sidebar-muted tabular-nums">
                      {displayPercent(place.electorate_share, 1)}
                    </span>
                  </span>
                </TableCell>
                <TableCell>
                  {duel ? (
                    <PartyShare map={map} partyId={duel.first.partyId} value={duel.first.value} digits={digits} />
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>
                  {duel?.second ? (
                    <PartyShare map={map} partyId={duel.second.partyId} value={duel.second.value} digits={digits} />
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell numeric>
                  {duel ? (
                    duel.tie ? (
                      <Badge variant="warning">
                        Empate · {duel.gap.toLocaleString("pt-BR", { maximumFractionDigits: digits })} p.p.
                      </Badge>
                    ) : (
                      `${duel.gap.toLocaleString("pt-BR", { maximumFractionDigits: digits })} p.p.`
                    )
                  ) : (
                    "—"
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {/* Rodapé */}
      {all.length > COLLAPSED_ROWS && (
        <div className="flex justify-center border-t border-muted p-2.5">
          <Button variant="link" size="sm" onClick={() => setExpanded((open) => !open)}>
            {expanded ? "Ver menos" : `Ver os ${all.length}`}
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </Button>
        </div>
      )}
    </Card>
  );
}
