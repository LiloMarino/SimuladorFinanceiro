import type { components } from "@/types/openapi";

export type Stock = Omit<components["schemas"]["CandleDTO"], "id">;

export type StockCandle = components["schemas"]["StockPriceHistoryDTO"];

export type StockDetails = Omit<components["schemas"]["StockDetailsDTO"], "id">;
