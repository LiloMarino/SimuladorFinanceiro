import { queryOptions } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type ApiError from "@/shared/lib/models/ApiError";
import type { SeriesCoverage } from "@/types";

export const seriesCoverageOptions = () =>
  queryOptions<SeriesCoverage[], ApiError>({
    queryKey: queryKeys.seriesCoverage(),
    queryFn: ({ signal }) => apiFetch<SeriesCoverage[]>("/api/import-assets/coverage", { signal }),
  });
