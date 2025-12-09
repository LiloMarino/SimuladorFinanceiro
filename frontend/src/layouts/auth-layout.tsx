import { useAuth } from "@/shared/hooks/useAuth";
import { Navigate, Outlet } from "react-router-dom";

export const AuthLayout = () => {
  const { loading, user } = useAuth();

  if (loading) return <div>Carregando...</div>;

  if (user) return <Navigate to="/" replace />;

  return <Outlet />;
};
