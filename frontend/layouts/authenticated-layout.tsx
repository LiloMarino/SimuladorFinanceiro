import { useAuth } from "@/shared/hooks/useAuth";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spinner } from "@/shared/components/ui/spinner";
import { useEffect } from "react";
import type { AuthRedirectState } from "./auth-layout";

export function AuthenticatedLayout() {
  const { loading, refresh, getSession } = useAuth();
  const location = useLocation();

  useEffect(() => {
    refresh();
    // #51
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </div>
    );
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
