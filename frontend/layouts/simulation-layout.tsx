import { Outlet, Navigate, useLocation } from "react-router-dom";
import { LoadingPage } from "@/pages/loading";
import { SimulationProvider } from "@/shared/context/simulation";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { RedirectState } from "@/types";

function SimulationGate() {
  const { simulation, loading } = useSimulation();
  const location = useLocation();

  if (loading) {
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

export function SimulationLayout() {
  return (
    <SimulationProvider>
      <SimulationGate />
    </SimulationProvider>
  );
}
