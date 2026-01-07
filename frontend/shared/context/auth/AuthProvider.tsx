import { useCallback, useEffect, type PropsWithChildren } from "react";
import { AuthContext } from "./AuthContext";
import type { Session } from "@/types/user";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

export function AuthProvider({ children }: PropsWithChildren) {
  // Consulta sessão atual
  const {
    data: session,
    setData: setSession,
    query: fetchSessionApi,
    loading: sessionLoading,
  } = useQueryApi<Session>("api/session/me", {
    initialFetch: false,
  });

  // Inicializa sessão
  const { mutate: initSessionApi, loading: initLoading } = useMutationApi("api/session/init");

  // Logout
  const { mutate: logoutApi, loading: logoutLoading } = useMutationApi("api/session/logout");

  const initSession = useCallback(async () => {
    await initSessionApi({});
    return fetchSessionApi();
  }, [initSessionApi, fetchSessionApi]);

  const refresh = useCallback(async () => {
    return fetchSessionApi();
  }, [fetchSessionApi]);

  const logout = useCallback(async () => {
    await logoutApi({});
    setSession(null);
  }, [logoutApi, setSession]);

  // Inicializa sessão ao montar
  useEffect(() => {
    void initSession();
  }, [initSession]);

  return (
    <AuthContext.Provider
      value={{
        getSession: () => session,
        getUser: () => session?.user ?? null,
        refresh,
        logout,
        loading: sessionLoading || initLoading || logoutLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
