import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { Outlet, useNavigate } from "react-router-dom";

export const AuthLayout = () => {
  const { loading, user } = useAuth();
  const navigate = useNavigate();

  if (loading)
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </div>
    );

  if (user) {
    navigate("/", { replace: true });
  }

  return <Outlet />;
};
