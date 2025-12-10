import { useAuth } from "@/shared/hooks/useAuth";
import { Outlet, useNavigate } from "react-router-dom";
import { Spinner } from "@/shared/components/ui/spinner";

export const AuthenticatedLayout = () => {
  const { loading, user } = useAuth();
  const navigate = useNavigate();

  if (loading)
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </div>
    );

  if (!user) {
    navigate("/login", { replace: true });
  }

  return <Outlet />;
};
