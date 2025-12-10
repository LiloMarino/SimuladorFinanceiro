import { useCallback, type ReactNode, useEffect } from "react";
import Cookies from "js-cookie";
import { AuthContext } from "./AuthContext";
import type { Session } from "@/types/user";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  // Consulta a sessão atual
  const {
    data: session,
    setData: setSession,
    query: fetchSessionApi,
    loading: sessionLoading,
  } = useQueryApi<Session>("api/session/me", {
    initialFetch: false,
  });

  // Inicializa a sessão
  const { mutate: initSessionApi, loading: initLoading } = useMutationApi<{ client_id: string }>("api/session/init");

  const initSession = useCallback(async () => {
    const initData = await initSessionApi({});
    Cookies.set("client_id", initData.client_id, { expires: 365 });
    return fetchSessionApi();
  }, [initSessionApi, fetchSessionApi]);

  const refresh = useCallback(async () => {
    const fetchedSession = await fetchSessionApi();
    return fetchedSession;
  }, [fetchSessionApi]);

  const logout = useCallback(() => {
    Cookies.remove("client_id");
    setSession(null);
  }, [setSession]);

  // Inicializa sessão ao montar
  useEffect(() => {
    void initSession();
  }, [initSession]);

  return (
    <AuthContext.Provider
      value={{
        getSession: () => session,
        getUser: () => session?.user ?? null,
        logout,
        refresh,
        loading: sessionLoading || initLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
