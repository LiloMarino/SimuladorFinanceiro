import { useAuth } from "@/shared/hooks/useAuth";
import { Navigate, Outlet } from "react-router-dom";
import { Spinner } from "@/shared/components/ui/spinner";

export const AuthenticatedLayout = () => {
  const { loading, user } = useAuth();

  if (loading)
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </div>
    );

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
