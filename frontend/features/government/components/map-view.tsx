import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { useElementWidth } from "@/shared/hooks/useElementWidth";
import { partyColor } from "@/shared/lib/party-colors";
import type { ElectionMap } from "@/types";
import type { MapLensId } from "../lib/map-lenses";
import type { LensView } from "../lib/map-fills";
import {
  classifyPlace,
  dayMonth,
  formatPercent,
  partyOf,
  placeByCode,
  placesOf,
  pollDateLabel,
  standings,
  type MapDivision,
} from "../lib/map-lenses";
import { CHANGE_SINCE, TECHNICAL_TIE } from "../lib/map-metrics";
import { BrazilMap } from "./brazil-map";

type MapViewProps = {
  map: ElectionMap;
  division: MapDivision;
  lens: MapLensId;
  view: LensView;
  selected: string;
  onSelect: (code: string) => void;
};

const MAX_MAP_WIDTH = 640;
const MIN_MAP_WIDTH = 250;

/** O mapa pintado pela lente, com a legenda, a frase que resume o que ele mostra e a data da pesquisa. */
export function MapView({ map, division, lens, view, selected, onSelect }: MapViewProps) {
  const [attachWidth, width] = useElementWidth<HTMLDivElement>();
  const mapWidth = Math.min(MAX_MAP_WIDTH, Math.max(MIN_MAP_WIDTH, width));
  const places = placesOf(map, division);
  const showResult = lens === "result";

  const footer = showResult
    ? map.result && `Apuração do ${map.result.round}º turno de ${pollDateLabel(map.result.date)}`
    : map.poll &&
      `Pesquisa de ${pollDateLabel(map.poll.date)}${map.poll.next_date ? ` · próxima em ${dayMonth(map.poll.next_date)}` : ""}`;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          {/* Título */}
          <div className="grid gap-1">
            <b className="text-[15px]">{view.title}</b>
            <p className="text-[13px] text-muted-foreground">{view.explanation}</p>
          </div>

          {/* Mapa */}
          <div ref={attachWidth} className="grid justify-items-center">
            {width > 0 && (
              <BrazilMap
                division={division}
                places={places}
                fills={view.fills}
                width={mapWidth}
                selected={selected}
                onSelect={onSelect}
                tip={(code) => <PlaceTip map={map} code={code} lens={lens} view={view} />}
              />
            )}
          </div>

          {/* Legenda */}
          <Legend map={map} lens={lens} view={view} />

          {view.sentence && <p className="text-[13px]">{view.sentence}</p>}

          {/* Rodapé */}
          <div className="border-t pt-3 text-xs text-muted-foreground">{footer}</div>
        </div>
      </CardContent>
    </Card>
  );
}

function Legend({ map, lens, view }: { map: ElectionMap; lens: MapLensId; view: LensView }) {
  const { legend } = view;
  if (legend.kind === "scale") {
    return (
      <div className="grid gap-1">
        <span className="h-2.5 rounded-full" style={{ background: legend.gradient }} />
        <div className="flex justify-between font-mono text-xs text-muted-foreground">
          <span>{legend.min}</span>
          <span>{legend.max}</span>
        </div>
        {lens === "change" && (
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
            O centro é zero: sem mudança
            <MetricHint metric={CHANGE_SINCE} />
          </span>
        )}
      </div>
    );
  }
  return (
    <ul className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[13px]">
      {legend.parties.map((party) => (
        <li key={party.id} className="inline-flex items-center gap-1.5">
          <span className="size-3 rounded-full" style={{ backgroundColor: partyColor(party) }} />
          {party.abbr}
        </li>
      ))}
      {legend.tie && (
        <li className="inline-flex items-center gap-1.5">
          <span
            className="size-3 rounded-full"
            style={{
              background: `repeating-linear-gradient(45deg, ${legend.parties
                .slice(0, 2)
                .map((party) => partyColor(party))
                .join(" 0 3px, ")} 3px 6px)`,
            }}
          />
          Empate técnico: a diferença cabe na margem
          <MetricHint metric={TECHNICAL_TIE} />
        </li>
      )}
      {legend.parties.length === 0 && map.poll === null && map.result === null && (
        <li className="text-muted-foreground">Sem pesquisa ainda.</li>
      )}
    </ul>
  );
}

function PlaceTip({ map, code, lens, view }: { map: ElectionMap; code: string; lens: MapLensId; view: LensView }) {
  const place = placeByCode(map, code);
  if (!place) return null;
  const heading = <b className="block text-[13px]">{place.name}</b>;

  if (lens !== "leads" && lens !== "result") {
    return (
      <>
        {heading}
        <span>
          {view.title.split(" · ")[0]}: {view.valueText[code] ?? "sem dado"}
        </span>
      </>
    );
  }

  const source = lens === "leads" ? "poll" : "result";
  const ranked = standings(map, code, source);
  const total = ranked.reduce((sum, row) => sum + row.points, 0);
  const line = ranked
    .slice(0, 3)
    .map((row) => {
      const value = source === "poll" ? row.points : total > 0 ? (row.points / total) * 100 : 0;
      return `${partyOf(map, row.partyId)?.abbr ?? "?"} ${formatPercent(value, source === "poll" ? 0 : 1)}`;
    })
    .join(" · ");

  if (source === "result") {
    return (
      <>
        {heading}
        <span className="block">{line}</span>
        <span className="block opacity-80">sem margem: vence quem tem mais voto</span>
      </>
    );
  }

  const verdict = classifyPlace(ranked, place.margin);
  const margin = place.margin;
  const lead = verdict?.lead.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  const detail =
    verdict?.kind === "leads"
      ? `empate? não: +${lead} > ±${margin}`
      : verdict
        ? `${verdict.of === 3 ? "empate entre 3" : "empate"}: +${lead} ≤ ±${margin}`
        : "";
  return (
    <>
      {heading}
      <span className="block">{line}</span>
      <span className="block opacity-80">
        margem ±{margin}
        {detail && ` · ${detail}`}
      </span>
    </>
  );
}
