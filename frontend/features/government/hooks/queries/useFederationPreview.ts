import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FederationPreview, PreviewFederationRequest } from "@/types";

/** O que a federação muda para o partido de quem propõe: soma na barreira, orientação, promessas, verba e rejeição. */
export function useFederationPreview(request: PreviewFederationRequest | null) {
  return useQuery({
    queryKey: queryKeys.federationPreview(request ?? {}),
    queryFn: ({ signal }) =>
      apiFetch<FederationPreview>("/api/government/federations/preview", { method: "POST", body: request, signal }),
    enabled: request !== null,
    placeholderData: keepPreviousData,
  });
}
