import type { CorrelationAssets } from "@/types";

type Asset = CorrelationAssets["assets"][number];

// O backend aceita até 20 tickers por matriz
export const MAX_TICKERS = 20;

const NO_SECTOR = "Sem setor";

/** Setores em ordem alfabética, com "Sem setor" no fim; tickers em ordem dentro de cada um. */
export function bySector(assets: Asset[]): [string, Asset[]][] {
  const groups = new Map<string, Asset[]>();
  for (const asset of assets) {
    const sector = asset.sector ?? NO_SECTOR;
    groups.set(sector, [...(groups.get(sector) ?? []), asset]);
  }
  return [...groups.entries()].sort(([a], [b]) => (a === NO_SECTOR ? 1 : b === NO_SECTOR ? -1 : a.localeCompare(b)));
}

/** O primeiro ticker de cada setor classificado: uma carteira de exemplo, diversificada por construção. */
export function oneOfEachSector(assets: Asset[]) {
  return bySector(assets)
    .filter(([sector]) => sector !== NO_SECTOR)
    .map(([, items]) => items[0].ticker)
    .slice(0, MAX_TICKERS);
}
