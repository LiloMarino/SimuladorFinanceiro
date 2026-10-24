import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PriceCorrectionResult } from "@/types";

export function useCorrectPriceErrors() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<PriceCorrectionResult>("/api/import-assets/correct-price-errors", { method: "POST" }),
    onSuccess: ({ corrected_days, stocks }) => {
      if (corrected_days === 0) {
        toast.success("Nenhum erro de dado encontrado", { description: "Os preços guardados já estão limpos." });
        return;
      }
      const days = corrected_days === 1 ? "1 dia corrigido" : `${corrected_days} dias corrigidos`;
      const assets = stocks === 1 ? "1 ativo" : `${stocks} ativos`;
      toast.success(`${days} em ${assets}`, {
        description: "O fechamento de cada um virou a interpolação entre os pregões vizinhos.",
      });
    },
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });
}
