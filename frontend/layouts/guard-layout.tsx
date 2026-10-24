import { Navigate, Outlet, matchPath, useLocation } from "react-router-dom";
import { LoadingPage } from "@/pages/loading";
import { useAuth } from "@/shared/hooks/useAuth";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { RedirectState } from "@/types";

export function GuardLayout() {
  const location = useLocation();
  const { session, loading: authLoading } = useAuth();
  const { simulation, loading: simulationLoading, failed, retry } = useSimulation();

  if (authLoading || simulationLoading || !simulation) {
    return <LoadingPage variant="fullscreen" failed={failed} onRetry={retry} />;
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
  const allowedWithoutSimulation = [
    "/lobby",
    "/backtest/new",
    "/backtest/running",
    "/import-assets",
    "/compare-simulations",
    "/correlation",
    "/achievements",
    "/match-result/:simulationId",
  ];
  if (isAuthenticated && !hasSimulation) {
    // O host de um backtest em andamento acompanha o andamento no lugar do lobby e da configuração
    const runsBacktest = simulation.backtest?.host_nickname === session?.user?.nickname;
    if (runsBacktest && (pathname === "/lobby" || pathname === "/backtest/new")) {
      return <Navigate to="/backtest/running" replace />;
    }
    if (!allowedWithoutSimulation.some((pattern) => matchPath(pattern, pathname))) {
      return <Navigate to="/lobby" replace state={{ from: { pathname } } satisfies RedirectState} />;
    }
    return <Outlet />;
  }

  // Autenticado + COM simulação + ainda fora dela → /join escolher a cor e entrar
  if (isAuthenticated && hasSimulation && session?.pending_join) {
    if (pathname !== "/join") {
      return <Navigate to="/join" replace />;
    }
    return <Outlet />;
  }

  // Autenticado + COM simulação: a Central de dados só abre fora da partida
  const blockedDuringSimulation = ["/login", "/lobby", "/import-assets", "/join"];
  if (isAuthenticated && hasSimulation) {
    if (blockedDuringSimulation.includes(pathname)) {
      return <Navigate to="/" replace />;
    }
    return <Outlet />;
  }

  return <Outlet />;
}
