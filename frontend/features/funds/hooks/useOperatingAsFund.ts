import { useActiveAccount } from "@/shared/hooks/useActiveAccount";

/** Verdadeiro quando a conta ativa é a de uma gestora e não a carteira pessoal. */
export function useOperatingAsFund() {
  return useActiveAccount().fund !== null;
}
