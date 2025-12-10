import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useEffect } from "react";
import { Navigate, Outlet } from "react-router-dom";

export function AuthLayout() {
  const { loading, getSession, refresh } = useAuth();

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (loading)
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </div>
    );

  if (getSession()?.authenticated) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
