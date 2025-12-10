import { useAuth } from "@/shared/hooks/useAuth";
import { Navigate, Outlet } from "react-router-dom";
import { Spinner } from "@/shared/components/ui/spinner";
import type { User } from "@/types";
import { useEffect, useState } from "react";

export function AuthenticatedLayout() {
  const { loading, getUser } = useAuth();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const user = await getUser();
      setUser(user);
    };
    fetchUser();
  }, [getUser]);

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
}
