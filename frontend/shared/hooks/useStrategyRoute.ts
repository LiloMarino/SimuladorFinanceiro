import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { strategyRoute, type StrategyRoute } from "@/shared/lib/strategy-route";

/** A rota do automático da conta que está no topo. */
export function useStrategyRoute(): StrategyRoute {
  const { active, accountsPending } = useActiveAccount();
  return strategyRoute(active, accountsPending);
}
