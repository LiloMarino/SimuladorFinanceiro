import { useCallback, useState, type ReactNode, useEffect } from "react";
import Cookies from "js-cookie";
import { AuthContext, type User } from "./AuthContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [clientId, setClientId] = useState<string | null>(null);

  const {
    data: meData,
    query: fetchMe,
    loading: meLoading,
  } = useQueryApi<{ user: User | null }>("api/session/me", { initialFetch: false });
  const { mutate: initSessionApi, loading: initSessionLoading } = useMutationApi<{ client_id: string }>(
    "api/session/init"
  );
  const { mutate: registerNicknameApi, loading: registerNicknameLoading } = useMutationApi<
    { user: User },
    { nickname: string }
  >("api/user/register");
  const { mutate: claimNicknameApi, loading: claimNicknameLoading } = useMutationApi<
    { user: User },
    { nickname: string }
  >("api/user/claim");

  const refresh = useCallback(async () => {
    await fetchMe();
  }, [fetchMe]);

  const initSession = useCallback(async () => {
    const data = await initSessionApi({});
    setClientId(data.client_id);
    Cookies.set("client_id", data.client_id, { expires: 365 });
    await refresh();
  }, [initSessionApi, refresh]);

  const registerNickname = useCallback(
    async (nickname: string) => {
      await registerNicknameApi({ nickname });
      await refresh();
    },
    [registerNicknameApi, refresh]
  );

  const claimNickname = useCallback(
    async (nickname: string) => {
      await claimNicknameApi({ nickname });
      await refresh();
    },
    [claimNicknameApi, refresh]
  );

  useEffect(() => {
    void initSession();
  }, [initSession]);

  return (
    <AuthContext.Provider
      value={{
        user: meData?.user ?? null,
        clientId,
        loading: meLoading || initSessionLoading || registerNicknameLoading || claimNicknameLoading,
        registerNickname,
        claimNickname,
        refresh,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
