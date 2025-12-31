import { useAuth } from "@/shared/hooks/useAuth";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";
import type { AuthRedirectState } from "./auth-layout";
import { LoadingPage } from "@/pages/loading";

export function AuthenticatedLayout() {
  const { loading, refresh, getSession } = useAuth();
  const location = useLocation();

  useEffect(() => {
    refresh();
    // #51
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return <LoadingPage variant="fullscreen" />;
  }

  if (!getSession()?.authenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={
          {
            from: { pathname: location.pathname },
          } satisfies AuthRedirectState
        }
      />
    );
  }

  return <Outlet />;
}
