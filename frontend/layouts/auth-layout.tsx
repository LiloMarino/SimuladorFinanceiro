import { LoadingPage } from "@/pages/loading";
import { useAuth } from "@/shared/hooks/useAuth";
import type { RedirectState } from "@/types";
import { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

export function AuthLayout() {
  const { loading, getSession, refresh } = useAuth();
  const location = useLocation();

  useEffect(() => {
    refresh();
    // #51
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return <LoadingPage variant="fullscreen" />;
  }

  if (getSession()?.authenticated) {
    const state = location.state as RedirectState | null;
    const redirectTo = state?.from?.pathname ?? "/";

    return <Navigate to={redirectTo} replace />;
  }

  return <Outlet />;
}
