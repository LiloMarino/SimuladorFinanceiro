import { Navigate, Outlet, matchPath, useLocation } from "react-router-dom";
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
  const allowedWithoutSimulation = ["/lobby", "/import-assets", "/compare-simulations", "/match-result/:simulationId"];
  if (isAuthenticated && !hasSimulation) {
    if (!allowedWithoutSimulation.some((pattern) => matchPath(pattern, pathname))) {
      return <Navigate to="/lobby" replace state={{ from: { pathname } } satisfies RedirectState} />;
    }
    return <Outlet />;
  }

  // Autenticado + COM simulação: a Central de dados só abre fora da partida
  const blockedDuringSimulation = ["/login", "/lobby", "/import-assets"];
  if (isAuthenticated && hasSimulation) {
    if (blockedDuringSimulation.includes(pathname)) {
      return <Navigate to="/" replace />;
    }
    return <Outlet />;
  }

  return <Outlet />;
}
