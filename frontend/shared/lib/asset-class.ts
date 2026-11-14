import type { AssetClass } from "@/types";

// Um rótulo por tipo da API: tipo novo sem rótulo não compila
export const ASSET_CLASS_LABELS: Record<AssetClass, string> = {
  STOCK: "Ações",
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
  CRYPTO: "Cripto",
  FUND: "Cotas de gestoras",
};

/** Os tipos de renda variável na ordem em que as telas os listam. */
export const ASSET_CLASSES = Object.keys(ASSET_CLASS_LABELS) as AssetClass[];
