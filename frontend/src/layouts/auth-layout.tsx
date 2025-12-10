import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { Navigate, Outlet } from "react-router-dom";

export const AuthLayout = () => {
  const { loading, user } = useAuth();

  if (loading)
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </div>
    );

  if (user) return <Navigate to="/" replace />;

  return <Outlet />;
};
