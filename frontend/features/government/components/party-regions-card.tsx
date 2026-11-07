import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayPercent } from "@/shared/lib/utils/display";
import { useElectionMap } from "../hooks/queries/useElectionMap";
import { lensView } from "../lib/map-fills";
import { DEFAULT_GROUP, formatPercent, paintedParty, placesOf, pointsOf, standings } from "../lib/map-lenses";
import { mapLink } from "../lib/map-url";
import { BrazilMap } from "./brazil-map";

const MAP_WIDTH = 250;

/** Onde o partido está bem: o mapa por região de quem lidera e a posição do partido em cada uma. */
export function PartyRegionsCard() {
  const { data: map } = useElectionMap();
  const party = map ? paintedParty(map, null) : undefined;
  if (!map?.poll || !party) return null;

  const regions = [...placesOf(map, "region")].sort((a, b) => b.electorate - a.electorate);
  const view = lensView(map, "region", "leads", party, DEFAULT_GROUP);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          {/* Título */}
          <h2 className="text-[15px] font-semibold">Onde o {party.abbr} está</h2>

          <div className="grid items-center gap-5 sm:grid-cols-[250px_minmax(0,1fr)]">
            {/* Mapa */}
            <BrazilMap
              division="region"
              places={regions}
              fills={view.fills}
              width={MAP_WIDTH}
              interactive={false}
              className="mx-auto"
            />

            {/* Regiões */}
            <div className="grid gap-2.5">
              <ul className="grid">
                {regions.map((region) => {
                  const ranked = standings(map, region.code, "poll");
                  const position = ranked.findIndex((row) => row.partyId === party.id) + 1;
                  return (
                    <li key={region.code} className="flex items-center justify-between gap-2 border-b py-2 text-[13px]">
                      <span>
                        {region.name}{" "}
                        <span className="text-xs text-muted-foreground">
                          {displayPercent(region.electorate_share, 1)}
                        </span>
                      </span>
                      <span className="flex items-center gap-2">
                        <b className="font-mono">{formatPercent(pointsOf(ranked, party.id))}</b>
                        {position > 0 && (
                          <Badge variant={position === 1 ? "success" : "secondary"} size="sm">
                            {position}º
                          </Badge>
                        )}
                      </span>
                    </li>
                  );
                })}
              </ul>
              <Button
                variant="ghost"
                size="sm"
                className="justify-self-start"
                nativeButton={false}
                render={<Link to={mapLink("leads", "region")} />}
              >
                Abrir no mapa
                <ArrowRight />
              </Button>
            </div>
          </div>

          <span className="text-xs text-muted-foreground">
            A porcentagem é a intenção de voto do {party.abbr} na região, na pesquisa mais recente; o número cinza ao
            lado do nome é a fatia do eleitorado do país que mora ali.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
