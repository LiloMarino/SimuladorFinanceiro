import { useCallback, type ReactNode, useEffect } from "react";
import Cookies from "js-cookie";
import { AuthContext } from "./AuthContext";
import type { Session, User } from "@/types/user";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  // Consulta a sessão atual
  const { query: fetchSession, loading: sessionLoading } = useQueryApi<Session>("api/session/me", {
    initialFetch: false,
  });

  // Inicializa a sessão
  const { mutate: initSessionApi, loading: initLoading } = useMutationApi<{ client_id: string }>("api/session/init");

  const initSession = useCallback(async () => {
    const initData = await initSessionApi({});
    Cookies.set("client_id", initData.client_id, { expires: 365 });
    return fetchSession();
  }, [initSessionApi, fetchSession]);

  const getSession = useCallback(async (): Promise<Session> => {
    return fetchSession();
  }, [fetchSession]);

  const getUser = useCallback(async (): Promise<User | null> => {
    const session = await fetchSession();
    return session.user ?? null;
  }, [fetchSession]);

  const logout = useCallback(() => {
    Cookies.remove("client_id");
  }, []);

  useEffect(() => {
    void initSession();
  }, [initSession]);
  return (
    <AuthContext.Provider
      value={{
        getSession,
        getUser,
        logout,
        loading: sessionLoading || initLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
