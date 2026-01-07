import { Navigate, Outlet, useLocation } from "react-router-dom";
import { LoadingPage } from "@/pages/loading";
import { useAuth } from "@/shared/hooks/useAuth";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { RedirectState } from "@/types";

export function GuardLayout() {
  const location = useLocation();
  const { session, loading: authLoading } = useAuth();
  const { simulation, loading: simulationLoading } = useSimulation();

  if (authLoading || simulationLoading || !simulation) {
    return <LoadingPage variant="fullscreen" />;
  }

  const pathname = location.pathname; // Página requisitada
  const isAuthenticated = !!session?.authenticated;
  const hasSimulation = simulation.active;

  /* =========================
     REGRAS DE REDIRECIONAMENTO
     ========================= */

  // Usuário não autenticado → /login
  if (!isAuthenticated) {
    if (pathname !== "/login") {
      return <Navigate to="/login" replace state={{ from: { pathname } } satisfies RedirectState} />;
    }
    return <Outlet />;
  }

  // Autenticado + SEM simulação → /lobby
  if (isAuthenticated && !hasSimulation) {
    if (pathname !== "/lobby") {
      return <Navigate to="/lobby" replace state={{ from: { pathname } } satisfies RedirectState} />;
    }
    return <Outlet />;
  }

  // Autenticado + COM simulação
  if (isAuthenticated && hasSimulation) {
    if (pathname === "/login" || pathname === "/lobby") {
      return <Navigate to="/" replace />;
    }
    return <Outlet />;
  }

  return <Outlet />;
}
