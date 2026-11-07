import { useEffect } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { CardState } from "@/shared/components/card-state";
import { InfoHint } from "@/shared/components/info-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import type { ElectionMap } from "@/types";
import { MapLensMenu } from "../components/map-lens-menu";
import { MapPlaceCard } from "../components/map-place-card";
import { MapPlacesTable } from "../components/map-places-table";
import { MapView } from "../components/map-view";
import { useElectionMap } from "../hooks/queries/useElectionMap";
import { countdownLabel, monthYear } from "../lib/election";
import { lensView } from "../lib/map-fills";
import {
  DEFAULT_GROUP,
  defaultPlace,
  fallbackLens,
  lensAvailability,
  MAP_LENS_BY_KEY,
  paintedParty,
  placesOf,
  pollDateLabel,
  type MapDivision,
  type MapLensId,
} from "../lib/map-lenses";
import {
  divisionFromParam,
  divisionToParam,
  groupFromParam,
  groupToParam,
  lensFromParam,
  lensToParam,
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
          <div className="grid gap-5">
            <Skeleton className="h-80" />
            <Skeleton className="h-64" />
          </div>
        </div>
      </CardState>
    );
  }
  return <MapContent map={map} />;
}

function MapContent({ map }: { map: ElectionMap }) {
  const [params, setParams] = useSearchParams();
  const { data: state } = useSimulationState();

  const division: MapDivision = divisionFromParam(params.get("divisao")) ?? "state";
  const lens = fallbackLens(map, lensFromParam(params.get("lente")) ?? "leads");
  const partyParam = Number(params.get("partido"));
  const party = paintedParty(map, Number.isInteger(partyParam) && partyParam > 0 ? partyParam : null);
  const group = groupFromParam(params.get("grupo")) ?? DEFAULT_GROUP;
  const place =
    placesOf(map, division).find((item) => item.code === params.get("lugar")) ?? defaultPlace(map, division);

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

  // As teclas 1 a 6 trocam a lente em qualquer ponto da página
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      const target = event.target;
      if (target instanceof HTMLElement && target.matches("input, textarea, select, [contenteditable]")) return;
      const wanted = MAP_LENS_BY_KEY[event.key];
      if (!wanted || !lensAvailability(map, wanted).available) return;
      setParams(
        (previous) => {
          const next = new URLSearchParams(previous);
          next.set("lente", lensToParam(wanted));
          return next;
        },
        { replace: true },
      );
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [map, setParams]);

  const view = lensView(map, division, lens, party, group);
  const showResult = lens === "result";
  const today = state?.current_date;

  return (
    <div className="grid gap-5">
      {/* Cabeçalho */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <h1 className="inline-flex items-center gap-1.5 text-xl font-semibold">
          Mapa do Brasil
          <InfoHint>O eleitorado de cada estado e região, visto pela lente que você escolher.</InfoHint>
        </h1>
        {map.poll && <Badge variant="secondary">Pesquisa de {pollDateLabel(map.poll.date)}</Badge>}
        <Badge variant="secondary">
          Eleição de {monthYear(map.first_round)}
          {today ? ` · faltam ${countdownLabel(today, map.first_round)}` : ""}
        </Badge>
      </div>

      {!map.poll && !map.result && (
        <Alert variant="info">
          <AlertDescription>
            Sem pesquisa, as lentes da eleição ficam apagadas com a data em que abrem. Rejeição, aprovação e eleitorado
            já funcionam.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid items-start gap-5 xl:grid-cols-[256px_minmax(0,1fr)_340px]">
        <MapLensMenu
          map={map}
          division={division}
          onDivisionChange={(next) => update({ divisao: divisionToParam(next), lugar: null })}
          lens={lens}
          onLensChange={(next: MapLensId) => update({ lente: lensToParam(next) })}
          party={party}
          onPartyChange={(id) => update({ partido: String(id) })}
          group={group}
          onGroupChange={(next) => update({ grupo: groupToParam(next) })}
        />
        <MapView
          map={map}
          division={division}
          lens={lens}
          view={view}
          selected={place.code}
          onSelect={(code) => update({ lugar: code })}
        />
        <div className="grid gap-5">
          <MapPlaceCard map={map} place={place} showResult={showResult} />
          <MapPlacesTable
            map={map}
            division={division}
            party={party}
            selected={place.code}
            onSelect={(code) => update({ lugar: code })}
            showResult={showResult}
          />
        </div>
      </div>
    </div>
  );
}
