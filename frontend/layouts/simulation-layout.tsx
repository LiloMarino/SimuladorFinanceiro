import { Outlet, Navigate, useLocation } from "react-router-dom";
import { LoadingPage } from "@/pages/loading";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { RedirectState } from "@/types";

export function SimulationLayout() {
  const { simulation, loading } = useSimulation();
  const location = useLocation();

  if (loading || !simulation) {
    return <LoadingPage variant="fullscreen" />;
  }

  if (!simulation.active) {
    return (
      <Navigate
        to="/lobby"
        replace
        state={
          {
            from: { pathname: location.pathname },
          } satisfies RedirectState
        }
      />
    );
  }

  return <Outlet />;
}
