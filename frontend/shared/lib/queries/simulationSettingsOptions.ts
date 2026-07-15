import { queryOptions } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type ApiError from "@/shared/lib/models/ApiError";
import type { SimulationSettings } from "@/types";

export const simulationSettingsOptions = () =>
  queryOptions<SimulationSettings, ApiError>({
    queryKey: queryKeys.simulationSettings(),
    queryFn: ({ signal }) => apiFetch<SimulationSettings>("/api/simulation/settings", { signal }),
  });
