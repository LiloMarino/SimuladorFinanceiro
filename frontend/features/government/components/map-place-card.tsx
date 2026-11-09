import type { ReactNode } from "react";
import { MetricHint } from "@/shared/components/metric-hint";
import { PartyMark } from "@/shared/components/party-mark";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Separator } from "@/shared/components/ui/separator";
import { cn } from "@/shared/lib/utils";
import { partyColor } from "@/shared/lib/party-colors";
import { displayPercent } from "@/shared/lib/utils/display";
import type { ElectionMap, MapPlace, VoterGroup } from "@/types";
import { PLACE_MARGIN } from "../lib/map-metrics";
import {
  changeOf,
  classifyPlace,
  dayMonth,
  formatPercent,
  groupShare,
  momentSource,
  nationalGroupShare,
  partyOf,
  placeByCode,
  previousDate,
  standings,
} from "../lib/map-lenses";
import { GROUP_INFO } from "../lib/voters";

type MapPlaceCardProps = {
  map: ElectionMap;
  place: MapPlace;
  /** O gráfico do lugar ao longo da campanha; só existe com a linha do tempo à vista. */
  trend?: ReactNode;
};

type Row = { partyId: number; value: number; change: number | null };

/** Uma linha por partido: a pesquisa com a margem do lugar ou, sem pesquisa, a apuração em votos válidos. */
function rowsOf(map: ElectionMap, place: MapPlace, source: "poll" | "result"): Row[] {
  const ranked = standings(map, place.code, source);
  const total = ranked.reduce((sum, row) => sum + row.points, 0);
  return ranked.map((row) => ({
    partyId: row.partyId,
    value: source === "poll" ? row.points : total > 0 ? (row.points / total) * 100 : 0,
    change: changeOf(map, place.code, row.partyId),
  }));
}

function signedArrow(change: number) {
  const rounded = Math.round(change);
  if (rounded === 0) return { text: "=", className: "text-muted-foreground" };
  return rounded > 0
    ? { text: `▲${rounded}`, className: "text-success" }
    : { text: `▼${Math.abs(rounded)}`, className: "text-destructive" };
}

/** O lugar selecionado: tamanho, quem lidera, a intenção de voto com a margem e os grupos que votam ali. */
export function MapPlaceCard({ map, place, trend }: MapPlaceCardProps) {
  const source = momentSource(map);
  const previous = previousDate(map);
  const region = place.region ? placeByCode(map, place.region) : undefined;
  const rows = source ? rowsOf(map, place, source) : [];
  const margin = source === "poll" ? place.margin : 0;
  const scaleMax = Math.max(1, ...rows.map((row) => row.value + margin));
  const undecided =
    source === "poll" ? Number(map.poll?.places.find((item) => item.code === place.code)?.undecided ?? 0) : 0;
  const verdict = source ? classifyPlace(standings(map, place.code, source), margin) : null;
  const leaderAbbr = verdict?.kind === "leads" ? partyOf(map, verdict.leader)?.abbr : undefined;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          {/* Cabeçalho do lugar */}
          <div className="grid gap-1">
            <b className="text-lg">{place.name}</b>
            <span className="text-[13px] text-muted-foreground">
              {region ? `${region.name} · ` : ""}
              {displayPercent(place.electorate_share, 1)} do eleitorado ·{" "}
              {(place.electorate / 1_000_000).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mi
            </span>
            {verdict && (
              <div className="pt-1">
                {verdict.kind === "leads" ? (
                  <Badge variant="success">
                    {leaderAbbr} {source === "result" ? "venceu" : "à frente"} por{" "}
                    {verdict.lead.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} p.p.
                  </Badge>
                ) : (
                  <Badge variant="warning">{verdict.of === 3 ? "Empate entre 3" : "Empate técnico"}</Badge>
                )}
              </div>
            )}
          </div>

          {/* Intenção de voto */}
          {source ? (
            <div className="grid gap-2">
              <div className="flex items-center justify-between gap-2 text-[13px]">
                <span className="inline-flex items-center gap-1 font-semibold">
                  {source === "poll" ? `Intenção de voto · margem ±${margin}` : "Votos válidos da apuração"}
                  {source === "poll" && <MetricHint metric={PLACE_MARGIN} />}
                </span>
                {previous && <span className="text-xs text-muted-foreground">▲▼ desde {dayMonth(previous)}</span>}
              </div>
              <ul className="grid gap-1.5">
                {rows.map((row) => {
                  const party = partyOf(map, row.partyId);
                  if (!party) return null;
                  const color = partyColor(party);
                  const arrow = row.change === null ? null : signedArrow(row.change);
                  return (
                    <li key={row.partyId} className="grid grid-cols-[3.25rem_1fr_3rem_2.5rem] items-center gap-2">
                      <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                      <span className="relative h-3 rounded-full bg-muted">
                        {margin > 0 && (
                          <span
                            className="absolute inset-y-0 rounded-full opacity-[.22]"
                            style={{
                              backgroundColor: color,
                              left: `${(Math.max(0, row.value - margin) / scaleMax) * 100}%`,
                              width: `${((Math.min(scaleMax, row.value + margin) - Math.max(0, row.value - margin)) / scaleMax) * 100}%`,
                            }}
                          />
                        )}
                        <span
                          className="absolute inset-y-0 left-0 rounded-full"
                          style={{ backgroundColor: color, width: `${(row.value / scaleMax) * 100}%` }}
                        />
                      </span>
                      <span className="text-right font-mono text-[13px] font-semibold">
                        {formatPercent(row.value, source === "poll" ? 0 : 1)}
                      </span>
                      <span className={cn("text-right font-mono text-xs", arrow?.className)}>{arrow?.text}</span>
                    </li>
                  );
                })}
                {source === "poll" && (
                  <li className="grid grid-cols-[3.25rem_1fr_3rem_2.5rem] items-center gap-2 text-xs text-muted-foreground">
                    <span>Indec.</span>
                    <span />
                    <span className="text-right font-mono">{formatPercent(undecided)}</span>
                    <span />
                  </li>
                )}
              </ul>
            </div>
          ) : (
            <p className="text-[13px] text-muted-foreground">
              Sem pesquisa ainda: a primeira abre em {dayMonth(map.opens_on)}.
            </p>
          )}

          {/* Ao longo da campanha */}
          {trend}

          <Separator />

          {/* Quem vota aqui */}
          <GroupBars map={map} place={place} />
        </div>
      </CardContent>
    </Card>
  );
}

function GroupBars({ map, place }: { map: ElectionMap; place: MapPlace }) {
  const groups = Object.keys(GROUP_INFO) as VoterGroup[];
  // Do grupo mais distante da média do país ao mais parecido com ela
  const shares = groups
    .map((group) => ({
      group,
      here: groupShare(place, group),
      country: nationalGroupShare(map, group),
    }))
    .sort((a, b) => Math.abs(b.here - b.country) - Math.abs(a.here - a.country));
  const scaleMax = Math.max(1, ...shares.flatMap((row) => [row.here, row.country]));
  const biggest = shares.reduce((best, row) => (row.here / row.country > best.here / best.country ? row : best));
  const ratio = biggest.country > 0 ? biggest.here / biggest.country : 1;
  const comparison =
    ratio >= 2 ? "mais que o dobro do país" : ratio >= 1.2 ? "acima do país" : "perto da média do país";

  return (
    <div className="grid gap-2">
      <span className="text-[13px] font-semibold">
        Quem vota aqui <span className="font-normal text-muted-foreground">· o traço é a média do país</span>
      </span>
      <ul className="grid gap-1.5">
        {shares.map((row) => (
          <li key={row.group} className="grid grid-cols-[6.5rem_1fr_2.5rem] items-center gap-2 text-[13px]">
            <span className="truncate text-muted-foreground">{GROUP_INFO[row.group].short}</span>
            <span className="relative h-2.5 rounded-full bg-muted">
              <span
                className="absolute inset-y-0 left-0 rounded-full bg-info"
                style={{ width: `${(row.here / scaleMax) * 100}%` }}
              />
              <span
                className="absolute -inset-y-0.5 w-0.5 bg-foreground"
                style={{ left: `${(row.country / scaleMax) * 100}%` }}
              />
            </span>
            <span className="text-right font-mono font-semibold">{formatPercent(row.here)}</span>
          </li>
        ))}
      </ul>
      <p className="text-xs text-muted-foreground">
        {place.name}: {GROUP_INFO[biggest.group].label.toLowerCase()} é {formatPercent(biggest.here)} do eleitorado,{" "}
        {comparison} ({formatPercent(biggest.country)}).
      </p>
    </div>
  );
}
