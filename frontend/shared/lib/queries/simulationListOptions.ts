import { queryOptions } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type ApiError from "@/shared/lib/models/ApiError";
import type { SimulationListItem } from "@/types";

export const simulationListOptions = () =>
  queryOptions<SimulationListItem[], ApiError>({
    queryKey: queryKeys.simulationList(),
    queryFn: ({ signal }) => apiFetch<SimulationListItem[]>("/api/simulation/list", { signal }),
  });
