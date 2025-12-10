import { useCallback, useState, type ReactNode, useEffect } from "react";
import Cookies from "js-cookie";
import { AuthContext } from "./AuthContext";
import type { Session } from "@/types/user";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [clientId, setClientId] = useState<string | null>(null);

  const {
    data: sessionData,
    query: fetchMe,
    loading: meLoading,
  } = useQueryApi<Session>("api/session/me", { initialFetch: false });

  const { mutate: initSessionApi, loading: initSessionLoading } = useMutationApi<{ client_id: string }>(
    "api/session/init"
  );
  const refresh = useCallback(async () => {
    await fetchMe();
  }, [fetchMe]);

  const initSession = useCallback(async () => {
    const data = await initSessionApi({});
    setClientId(data.client_id);
    Cookies.set("client_id", data.client_id, { expires: 365 });
    await refresh();
  }, [initSessionApi, refresh]);

  useEffect(() => {
    void initSession();
  }, [initSession]);

  return (
    <AuthContext.Provider
      value={{
        user: sessionData?.user ?? null,
        clientId,
        loading: meLoading || initSessionLoading,
        refresh,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
