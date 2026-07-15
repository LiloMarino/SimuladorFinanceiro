import { queryOptions } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type ApiError from "@/shared/lib/models/ApiError";
import type { EconomicIndicators } from "@/types";

export const economicIndicatorsOptions = () =>
  queryOptions<EconomicIndicators, ApiError>({
    queryKey: queryKeys.economicIndicators(),
    queryFn: ({ signal }) => apiFetch<EconomicIndicators>("/api/economic-indicators", { signal }),
  });
