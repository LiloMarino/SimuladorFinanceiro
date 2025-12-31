import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

export type AuthRedirectState = {
  from?: {
    pathname: string;
  };
};

export function AuthLayout() {
  const { loading, getSession, refresh } = useAuth();
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

  if (getSession()?.authenticated) {
    const state = location.state as AuthRedirectState | null;
    const redirectTo = state?.from?.pathname ?? "/";

    return <Navigate to={redirectTo} replace />;
  }

  return <Outlet />;
}
