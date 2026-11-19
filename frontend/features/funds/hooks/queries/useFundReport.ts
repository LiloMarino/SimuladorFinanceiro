import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { fundKeys } from "@/shared/hooks/fund-keys";
import type { FundMonthlyReport } from "@/types";

/** O relatório de um mês fechado (`month` no formato "2026-10"); o último mês publicado vem quando `month` é nulo. */
export function useFundReport(fundId: number, month: string | null) {
  return useQuery({
    queryKey: fundKeys.report(fundId, month ?? "last"),
    queryFn: ({ signal }) => apiFetch<FundMonthlyReport>(`/api/funds/${fundId}/reports/${month}`, { signal }),
    enabled: month !== null,
    placeholderData: keepPreviousData,
  });
}
