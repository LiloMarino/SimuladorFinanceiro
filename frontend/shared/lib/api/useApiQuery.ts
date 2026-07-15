import { useQuery, type UseQueryOptions, type QueryKey } from "@tanstack/react-query";
import type ApiError from "@/shared/lib/models/ApiError";

/** useQuery com TError fixo em ApiError, já que `apiFetch` sempre rejeita com ApiError. */
export function useApiQuery<TQueryFnData, TData = TQueryFnData, TQueryKey extends QueryKey = QueryKey>(
  options: UseQueryOptions<TQueryFnData, ApiError, TData, TQueryKey>
) {
  return useQuery(options);
}
