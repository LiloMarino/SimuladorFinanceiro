import { ChevronDown } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { Kbd } from "@/shared/components/ui/kbd";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Separator } from "@/shared/components/ui/separator";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { partyColor } from "@/shared/lib/party-colors";
import { displayMonthShort } from "@/shared/lib/utils/display";
import type { ElectionMap, MapParty, VoterGroup } from "@/types";
import { scaleEnds, scaleGradient } from "../lib/map-fills";
import {
  lensAvailability,
  MAP_LENSES,
  MAP_SECTIONS,
  type MapDivision,
  type MapLens,
  type MapLensId,
} from "../lib/map-lenses";
import { GROUP_INFO } from "../lib/voters";

type MapLensMenuProps = {
  map: ElectionMap;
  division: MapDivision;
  onDivisionChange: (division: MapDivision) => void;
  lens: MapLensId;
  onLensChange: (lens: MapLensId) => void;
  /** O partido pintado nas lentes do partido. */
  party: MapParty | undefined;
  onPartyChange: (partyId: number) => void;
  group: VoterGroup;
  onGroupChange: (group: VoterGroup) => void;
};

const CAPTION = "text-xs font-semibold tracking-wide text-muted-foreground uppercase";

// Os partidos viram faixas de cor lado a lado, no ícone das lentes de quem lidera
function stripes(parties: MapParty[]) {
  const colors = parties.slice(0, 3).map((party) => partyColor(party));
  if (colors.length < 2) return colors[0] ?? "var(--muted)";
  const step = 100 / colors.length;
  const stops = colors.map((color, index) => `${color} ${index * step}% ${(index + 1) * step}%`);
  return `linear-gradient(90deg, ${stops.join(", ")})`;
}

/** As lentes do mapa agrupadas por assunto, com a divisão (região ou estado) e as escolhas de cada lente. */
export function MapLensMenu({
  map,
  division,
  onDivisionChange,
  lens,
  onLensChange,
  party,
  onPartyChange,
  group,
  onGroupChange,
}: MapLensMenuProps) {
  const swatch = (item: MapLens) =>
    item.id === "leads" || item.id === "result"
      ? stripes(map.parties)
      : scaleGradient(scaleEnds(item.id, party, group));

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <b className="text-[15px]">Lentes do mapa</b>

          {/* Divisão */}
          <div className="grid gap-1.5">
            <span className={CAPTION}>Dividir por</span>
            <ToggleGroup
              variant="segmented"
              className="w-full"
              value={[division]}
              onValueChange={(value) => value[0] && onDivisionChange(value[0] as MapDivision)}
            >
              <ToggleGroupItem value="region" className="flex-1">
                Região
              </ToggleGroupItem>
              <ToggleGroupItem value="state" className="flex-1">
                Estado
              </ToggleGroupItem>
            </ToggleGroup>
          </div>

          <Separator />

          {/* Lentes */}
          <ToggleGroup
            variant="list"
            size="list"
            orientation="vertical"
            className="w-full"
            value={[lens]}
            onValueChange={(value) => value[0] && onLensChange(value[0] as MapLensId)}
          >
            {MAP_SECTIONS.map((section) => (
              <div key={section} className="grid gap-0.5 pt-1.5 first:pt-0">
                <div className="flex items-center justify-between px-1 pb-0.5">
                  <span className={CAPTION}>{section}</span>
                  {section === "Seu partido" && party && map.parties.length > 1 && (
                    <PartyChoice parties={map.parties} party={party} onChange={onPartyChange} />
                  )}
                </div>
                {MAP_LENSES.filter((item) => item.section === section).map((item) => {
                  const availability = lensAvailability(map, item.id);
                  return (
                    <ToggleGroupItem key={item.id} value={item.id} disabled={!availability.available}>
                      <span aria-hidden className="size-4 shrink-0 rounded-sm" style={{ background: swatch(item) }} />
                      {item.id === "change" && map.poll?.previous_date
                        ? `Variação desde ${displayMonthShort(map.poll.previous_date)}`
                        : item.label}
                      {availability.available ? (
                        item.key && <Kbd>{item.key}</Kbd>
                      ) : (
                        <span className="ml-auto text-xs">{availability.reason}</span>
                      )}
                    </ToggleGroupItem>
                  );
                })}
              </div>
            ))}
          </ToggleGroup>

          {/* Grupo da lente do eleitorado */}
          {lens === "group" && (
            <RadioGroup dense value={group} onValueChange={(value) => onGroupChange(value as VoterGroup)}>
              {(Object.keys(GROUP_INFO) as VoterGroup[]).map((item) => (
                <label key={item} className="flex cursor-pointer items-center gap-2 px-3 py-1 text-[13px]">
                  <RadioGroupItem value={item} />
                  {GROUP_INFO[item].label}
                </label>
              ))}
            </RadioGroup>
          )}

          <Separator />

          <p className="text-xs text-muted-foreground">
            As teclas 1 a 6 trocam a lente. Toda lente sai do mesmo eleitorado em grupos: muda só a pergunta que o mapa
            responde.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

type PartyChoiceProps = { parties: MapParty[]; party: MapParty; onChange: (partyId: number) => void };

function PartyChoice({ parties, party, onChange }: PartyChoiceProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" size="xs" aria-label="Trocar o partido do mapa" />}>
        <PartyMark abbr={party.abbr} color={party.color} size="sm" />
        <ChevronDown className="size-3.5" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {parties.map((item) => (
          <DropdownMenuItem
            key={item.id}
            variant={item.id === party.id ? "selected" : "default"}
            onClick={() => onChange(item.id)}
          >
            <PartyMark abbr={item.abbr} color={item.color} size="sm" />
            {item.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
