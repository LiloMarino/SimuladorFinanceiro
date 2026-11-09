import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { partyColor } from "@/shared/lib/party-colors";
import type { ElectionMap, ElectionRound } from "@/types";
import { useElectionMap } from "../hooks/queries/useElectionMap";
import { lensView } from "../lib/map-fills";
import {
  DEFAULT_GROUP,
  extremes,
  formatPercent,
  partyOf,
  placeByCode,
  placesOf,
  pointsOf,
  standings,
  statesWon,
  votesInMillions,
  type MapDivision,
} from "../lib/map-lenses";
import { BrazilMap } from "./brazil-map";

const MAP_WIDTH = 330;

type RoundResultMapProps = { result: ElectionRound };

/** A apuração do turno no mapa: quem venceu em cada estado. */
export function RoundResultMap({ result }: RoundResultMapProps) {
  const { data: map } = useElectionMap();
  // O mapa guarda o último turno apurado: só ele ilustra o resultado aberto
  if (!map?.result || map.result.round !== result.round) return null;

  const states = placesOf(map, "state");
  // O resultado do turno aberto: sem a pesquisa de hoje, "Quem lidera" é "Quem venceu"
  const view = lensView({ ...map, poll: null }, "state", "leads", undefined, DEFAULT_GROUP);
  const ranking = [...statesWon(map).entries()]
    .map(([partyId, count]) => ({ party: partyOf(map, partyId), count }))
    .sort((a, b) => b.count - a.count);

  return (
    <div className="grid gap-2">
      <span className="text-xs font-semibold text-muted-foreground">Quem venceu em cada lugar</span>
      <div className="grid items-center gap-4 sm:grid-cols-[330px_minmax(0,1fr)]">
        <BrazilMap
          division="state"
          places={states}
          fills={view.fills}
          width={MAP_WIDTH}
          interactive={false}
          className="mx-auto"
        />
        <ul className="grid gap-2 text-[13px]">
          {ranking.map(({ party, count }) =>
            party ? (
              <li key={party.id} className="flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-2">
                  <span className="size-3 rounded-full" style={{ backgroundColor: partyColor(party) }} />
                  {party.abbr}
                </span>
                <b className="font-mono">
                  {count} {count === 1 ? "estado" : "estados"}
                </b>
              </li>
            ) : null,
          )}
          <li className="pt-1 text-xs text-muted-foreground">
            No resultado não há margem: a cor é cheia. Quem vence é o voto do país, não o número de estados.
          </li>
        </ul>
      </div>
    </div>
  );
}

/** O melhor e o pior lugar do partido do jogador no turno, para quem tem partido na disputa. */
export function RoundResultSentence({ result }: RoundResultMapProps) {
  const { data: map } = useElectionMap();
  if (!map?.result || map.result.round !== result.round) return null;
  const party = map.viewer_party_id === null ? undefined : partyOf(map, map.viewer_party_id);
  const national = party && result.parties.find((row) => row.party_id === party.id);
  if (!party || !national) return null;
  return <ViewerSentence map={map} points={Number(national.share) * 100} partyId={party.id} abbr={party.abbr} />;
}

type ViewerSentenceProps = { map: ElectionMap; points: number; partyId: number; abbr: string };

// A fatia do partido em cada lugar é a dos votos válidos da apuração
function ViewerSentence({ map, points, partyId, abbr }: ViewerSentenceProps) {
  const shareByPlace = (division: MapDivision) =>
    Object.fromEntries(
      placesOf(map, division).map((place) => {
        const ranked = standings(map, place.code, "result");
        const total = ranked.reduce((sum, row) => sum + row.points, 0);
        return [place.code, total > 0 ? (pointsOf(ranked, partyId) / total) * 100 : 0];
      }),
    );
  const states = extremes(shareByPlace("state"));
  const regions = extremes(shareByPlace("region"));
  if (!states || !regions) return null;

  const electorate = placesOf(map, "state").reduce((sum, place) => sum + place.electorate, 0);
  const name = (code: string) => placeByCode(map, code)?.name ?? code;

  return (
    <Alert variant="success">
      <AlertTitle>
        O {abbr} foi melhor em {name(states.max.code)} ({formatPercent(states.max.value)}) e em {name(regions.max.code)}{" "}
        ({formatPercent(regions.max.value)})
      </AlertTitle>
      <AlertDescription>
        Pior em {name(states.min.code)} ({formatPercent(states.min.value)}) e em {name(regions.min.code)} (
        {formatPercent(regions.min.value)}). No país, {formatPercent(points)} dos votos válidos:{" "}
        {votesInMillions(points, electorate).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mi de votos.
      </AlertDescription>
    </Alert>
  );
}
