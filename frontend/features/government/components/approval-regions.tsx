import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { useElectionMap } from "../hooks/queries/useElectionMap";
import { lensView } from "../lib/map-fills";
import {
  DEFAULT_GROUP,
  extremes,
  formatPercent,
  lensValues,
  paintedParty,
  placeByCode,
  placesOf,
} from "../lib/map-lenses";
import { mapLink } from "../lib/map-url";
import { BrazilMap } from "./brazil-map";

const MAP_WIDTH = 210;

/** A aprovação do governo por região: o mapa pequeno, a melhor e a pior região e a escala. */
export function ApprovalRegions() {
  const { data: map } = useElectionMap();
  if (!map?.approval) return null;

  const view = lensView(map, "region", "approval", paintedParty(map, null), DEFAULT_GROUP);
  const range = extremes(lensValues(map, "region", "approval", null, DEFAULT_GROUP));
  const best = range && placeByCode(map, range.max.code);
  const worst = range && placeByCode(map, range.min.code);
  if (!range || !best || !worst || view.legend.kind !== "scale") return null;

  return (
    <div className="grid items-center gap-5 sm:grid-cols-[210px_minmax(0,1fr)]">
      {/* Mapa */}
      <BrazilMap
        division="region"
        places={placesOf(map, "region")}
        fills={view.fills}
        width={MAP_WIDTH}
        interactive={false}
        className="mx-auto"
      />

      {/* Melhor e pior região */}
      <div className="grid gap-2 text-[13px]">
        <span className="text-xs font-semibold text-muted-foreground">Melhor e pior região</span>
        <div className="flex justify-between">
          <span>{best.name}</span>
          <b className="font-mono text-success">{formatPercent(range.max.value)}</b>
        </div>
        <div className="flex justify-between">
          <span>{worst.name}</span>
          <b className="font-mono text-destructive">{formatPercent(range.min.value)}</b>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
          <span>{view.legend.min}</span>
          <span className="h-2.5 w-28 rounded-full" style={{ background: view.legend.gradient }} />
          <span>{view.legend.max}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="justify-self-start"
          nativeButton={false}
          render={<Link to={mapLink("approval", "region")} />}
        >
          Abrir no mapa
          <ArrowRight />
        </Button>
      </div>
    </div>
  );
}
