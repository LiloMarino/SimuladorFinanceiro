import type { VoterGroup } from "@/types";
import { GROUP_INFO } from "./voters";
import type { MapDivision, MapLensId } from "./map-lenses";

// O estado do mapa vive na URL: ?lente=&divisao=&partido=&grupo=&lugar=
const LENS_PARAM: Record<MapLensId, string> = {
  leads: "lidera",
  result: "resultado",
  performance: "desempenho",
  change: "variacao",
  rejection: "rejeicao",
  approval: "aprovacao",
  group: "grupo",
};

const DIVISION_PARAM: Record<MapDivision, string> = { state: "estado", region: "regiao" };

const GROUPS = Object.keys(GROUP_INFO) as VoterGroup[];

export function lensFromParam(value: string | null): MapLensId | null {
  const found = (Object.keys(LENS_PARAM) as MapLensId[]).find((lens) => LENS_PARAM[lens] === value);
  return found ?? null;
}

export function divisionFromParam(value: string | null): MapDivision | null {
  return value === DIVISION_PARAM.state ? "state" : value === DIVISION_PARAM.region ? "region" : null;
}

export function groupFromParam(value: string | null): VoterGroup | null {
  return GROUPS.find((group) => group.toLowerCase() === value) ?? null;
}

export function lensToParam(lens: MapLensId) {
  return LENS_PARAM[lens];
}

export function divisionToParam(division: MapDivision) {
  return DIVISION_PARAM[division];
}

export function groupToParam(group: VoterGroup) {
  return group.toLowerCase();
}

/** O endereço do mapa já com a lente e a divisão escolhidas. */
export function mapLink(lens: MapLensId, division: MapDivision) {
  const params = new URLSearchParams({ lente: LENS_PARAM[lens], divisao: DIVISION_PARAM[division] });
  return `/map?${params.toString()}`;
}
