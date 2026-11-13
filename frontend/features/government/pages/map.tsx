import { useEffect } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { CardState } from "@/shared/components/card-state";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { ElectionMap, TimelinePoint } from "@/types";
import { MapLensMenu } from "../components/map-lens-menu";
import { MapPlaceCard } from "../components/map-place-card";
import { MapPlaceTrend } from "../components/map-place-trend";
import { MapPlacesTable } from "../components/map-places-table";
import { MapTimeline } from "../components/map-timeline";
import { MapView } from "../components/map-view";
import { useElectionMap } from "../hooks/queries/useElectionMap";
import { useElectionTimeline } from "../hooks/queries/useElectionTimeline";
import { useTimelinePlayback } from "../hooks/useTimelinePlayback";
import { countdownLabel, monthYear } from "../lib/election";
import { lensView } from "../lib/map-fills";
import {
  DEFAULT_GROUP,
  defaultPlace,
  fallbackLens,
  isDatedLens,
  lensAvailability,
  MAP_LENS_BY_KEY,
  paintedParty,
  placesOf,
  type MapDivision,
  type MapLensId,
} from "../lib/map-lenses";
import { lastHappened, pointAt } from "../lib/map-timeline";
import {
  divisionFromParam,
  divisionToParam,
  groupFromParam,
  groupToParam,
  lensFromParam,
  lensToParam,
  pointFromParam,
  yearFromParam,
} from "../lib/map-url";

export default function MapPage() {
  usePageLabel("Mapa");
  const match = useSimulation().simulation?.simulation;

  // O mapa é da expansão do governo: sem ela a página volta ao início
  if (match && !match.government_enabled) return <ExpansionOff />;
  return <MapLoader />;
}

function ExpansionOff() {
  useEffect(() => {
    toast.info("O mapa só existe com a expansão do governo ligada nesta partida");
  }, []);
  return <Navigate to="/" replace />;
}

function MapLoader() {
  const { data: map, error, refetch } = useElectionMap();

  if (!map) {
    return (
      <CardState
        bare
        label="Carregando o mapa"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não foi possível carregar o mapa"
        errorDescription="A pesquisa e o resto da página continuam. Tente de novo em instantes."
      >
        <Skeleton className="h-16" />
        <div className="grid items-start gap-5 xl:grid-cols-[256px_minmax(0,1fr)_340px]">
          <Skeleton className="h-96" />
          <Skeleton className="h-[34rem]" />
          <Skeleton className="h-96" />
        </div>
        <Skeleton className="h-[26rem]" />
      </CardState>
    );
  }
  return <MapContent map={map} />;
}

// O badge do cabeçalho: entre os turnos conta para o 2º; nas demais fases, para o 1º
function nextTurnLabel(map: ElectionMap, today: string | undefined) {
  const betweenRounds = map.phase === "BETWEEN_ROUNDS";
  const target = betweenRounds ? map.runoff : map.first_round;
  const name = betweenRounds
    ? `2º turno em ${displayDayMonth(map.runoff)}`
    : `Eleição de ${monthYear(map.first_round)}`;
  return `${name}${today ? ` · faltam ${countdownLabel(today, target)}` : ""}`;
}

function MapContent({ map }: { map: ElectionMap }) {
  const [params, setParams] = useSearchParams();
  const { data: state } = useSimulationState();
  const {
    data: timeline,
    error: timelineError,
    refetch: refetchTimeline,
  } = useElectionTimeline(yearFromParam(params.get("ano")));

  const division: MapDivision = divisionFromParam(params.get("divisao")) ?? "state";
  const wantedLens = lensFromParam(params.get("lente")) ?? "leads";
  const partyParam = Number(params.get("partido"));
  const group = groupFromParam(params.get("grupo")) ?? DEFAULT_GROUP;

  // O presente é o último ponto que já aconteceu do ano em curso (no mandato, do último ano encerrado)
  const presentYear = [...(timeline?.years ?? [])].reverse().find((item) => item.status !== "UPCOMING")?.year;
  const points = timeline?.points ?? [];
  const selected = timeline && points.length > 0 ? pointAt(points, pointFromParam(params.get("ponto"))) : undefined;
  const todayPoint = lastHappened(points);
  const isToday = !timeline || !selected || (timeline.year === presentYear && selected.date === todayPoint?.date);

  // Fora do presente a eleição mostrada é a do ponto escolhido; as lentes sem data seguem no hoje
  const shown: ElectionMap =
    isDatedLens(wantedLens) && timeline && selected && !isToday
      ? { ...map, poll: selected.poll, result: selected.result, parties: timeline.parties }
      : map;
  const lens = fallbackLens(shown, wantedLens);
  const rulerVisible = isDatedLens(lens);
  const party = paintedParty(shown, Number.isInteger(partyParam) && partyParam > 0 ? partyParam : null);
  const place =
    placesOf(shown, division).find((item) => item.code === params.get("lugar")) ?? defaultPlace(shown, division);

  // Cada escolha vive na URL: o endereço reabre o mapa como está
  const update = (patch: Record<string, string | null>) =>
    setParams(
      (previous) => {
        const next = new URLSearchParams(previous);
        for (const [key, value] of Object.entries(patch)) {
          if (value === null) next.delete(key);
          else next.set(key, value);
        }
        return next;
      },
      { replace: true },
    );

  const selectPoint = (point: TimelinePoint) => update({ ponto: point.date });
  const playback = useTimelinePlayback({
    points,
    selectedIndex: selected ? points.indexOf(selected) : 0,
    todayIndex: todayPoint ? points.indexOf(todayPoint) : 0,
    enabled: rulerVisible && selected !== undefined,
    onSelect: selectPoint,
  });

  // Trocar de lente ou de ano pausa a reprodução
  const chooseLens = (next: MapLensId) => {
    playback.pause();
    update({ lente: lensToParam(next) });
  };
  const chooseYear = (year: number) => {
    playback.pause();
    update({ ano: String(year), ponto: null });
  };
  const backToToday = () => {
    playback.pause();
    update({ ano: null, ponto: null });
  };

  // As teclas 1 a 6 trocam a lente em qualquer ponto da página
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      const target = event.target;
      if (target instanceof HTMLElement && target.matches("input, textarea, select, [contenteditable]")) return;
      const wanted = MAP_LENS_BY_KEY[event.key];
      if (!wanted || !lensAvailability(shown, wanted).available) return;
      chooseLens(wanted);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const view = lensView(shown, division, lens, party, group);
  const today = state?.current_date;

  return (
    <div className="grid gap-5">
      {/* Cabeçalho */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <h1 className="inline-flex items-center gap-1.5 text-xl font-semibold">
          Mapa do Brasil
          <InfoHint>O eleitorado de cada estado e região, visto pela lente que você escolher.</InfoHint>
        </h1>
        <Badge variant="info">{nextTurnLabel(map, today)}</Badge>
      </div>

      {/* Linha do tempo */}
      {rulerVisible && (
        <MapTimeline
          timeline={timeline}
          error={timelineError}
          onRetry={() => void refetchTimeline()}
          selected={selected}
          isToday={isToday}
          playback={playback}
          focusParty={party?.id ?? null}
          regions={map.places.filter((item) => item.kind === "REGION")}
          onYear={chooseYear}
          onSelect={selectPoint}
          onToday={backToToday}
        />
      )}

      <div className="grid items-start gap-5 xl:grid-cols-[256px_minmax(0,1fr)_340px]">
        <MapLensMenu
          map={shown}
          division={division}
          onDivisionChange={(next) => update({ divisao: divisionToParam(next), lugar: null })}
          lens={lens}
          onLensChange={chooseLens}
          party={party}
          onPartyChange={(id) => update({ partido: String(id) })}
          group={group}
          onGroupChange={(next) => update({ grupo: groupToParam(next) })}
        />
        <MapView
          map={shown}
          division={division}
          lens={lens}
          view={view}
          selected={place.code}
          onSelect={(code) => update({ lugar: code })}
        />
        <MapPlaceCard
          map={shown}
          place={place}
          trend={
            rulerVisible && timeline && selected ? (
              <MapPlaceTrend
                timeline={timeline}
                place={place}
                selected={selected}
                focusParty={party?.id ?? null}
                onSelect={selectPoint}
              />
            ) : null
          }
        />
      </div>

      {/* Lista de lugares em faixa larga */}
      <MapPlacesTable
        map={shown}
        division={division}
        selected={place.code}
        onSelect={(code) => update({ lugar: code })}
      />
    </div>
  );
}
