import { useMutation, type UseMutationOptions } from "@tanstack/react-query";
import type ApiError from "@/shared/lib/models/ApiError";

/** useMutation com TError fixo em ApiError, já que `apiFetch` sempre rejeita com ApiError. */
export function useApiMutation<TData = unknown, TVariables = void, TContext = unknown>(
  options: UseMutationOptions<TData, ApiError, TVariables, TContext>
) {
  return useMutation(options);
}
