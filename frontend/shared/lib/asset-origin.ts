import type { AssetOrigin } from "@/types";

// Um rótulo por origem da API: origem nova sem rótulo não compila
export const ASSET_ORIGIN_LABELS: Record<AssetOrigin, string> = {
  DOMESTIC: "Nacional",
  FOREIGN: "Internacional",
};

/** As origens na ordem em que as telas as listam. */
export const ASSET_ORIGINS = Object.keys(ASSET_ORIGIN_LABELS) as AssetOrigin[];
