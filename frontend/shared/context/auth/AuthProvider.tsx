import { useCallback, useEffect, type PropsWithChildren } from "react";
import { AuthContext } from "./AuthContext";
import type { Session } from "@/types/user";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

export function AuthProvider({ children }: PropsWithChildren) {
  // Sessão atual
  const {
    data: session,
    setData: setSession,
    query: fetchSessionApi,
    loading: sessionLoading,
  } = useQueryApi<Session>("/api/session/me", {
    initialFetch: false,
  });

  // Inicializa uma nova sessão
  const { mutate: initSessionApi, loading: initLoading } = useMutationApi("/api/session/init");

  // Logout
  const { mutate: logoutApi, loading: logoutLoading } = useMutationApi("/api/session/logout");

  const initSession = useCallback(async () => {
    await initSessionApi({});
    return fetchSessionApi();
  }, [initSessionApi, fetchSessionApi]);

  const logout = useCallback(async () => {
    await logoutApi({});
    setSession(null);

    // Garante novo client_id após logout
    await initSessionApi({});
  }, [initSessionApi, logoutApi, setSession]);

  // Inicializa sessão apenas uma vez
  useEffect(() => {
    void initSession();
  }, [initSession]);

  return (
    <AuthContext.Provider
      value={{
        session,
        user: session?.user ?? null,
        refresh: fetchSessionApi,
        logout,
        loading: sessionLoading || initLoading || logoutLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
