import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toFormData } from "@/shared/lib/api/toFormData";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ImportResult } from "@/types";
import { toastReplacedGenerated } from "../../lib/replaced-toast";

export type Source = "YFINANCE" | "CSV";
export type ImportRequest = { source: Source; ticker: string; overwrite: boolean; file: File | null };

export function useImportAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (req: ImportRequest) =>
      req.source === "CSV"
        ? apiFetch<ImportResult>("/api/import-assets/csv", {
            method: "POST",
            body: toFormData({ ticker: req.ticker, overwrite: req.overwrite, csv_file: req.file }),
          })
        : apiFetch<ImportResult>("/api/import-assets/yfinance", {
            method: "POST",
            body: { ticker: req.ticker, overwrite: req.overwrite },
          }),
    onSuccess: ({ coverage, replaced }) => toastReplacedGenerated(coverage.key, replaced),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });
}
