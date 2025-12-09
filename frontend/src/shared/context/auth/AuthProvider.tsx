import { useState, useEffect, type ReactNode } from "react";
import Cookies from "js-cookie";
import { AuthContext, type User } from "./AuthContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [clientId, setClientId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const { query: fetchMe } = useQueryApi<{ user: User | null }>("/session/me", { initialFetch: false });
  const { mutate: initSessionApi } = useMutationApi<{ client_id: string }>("/session/init", { method: "POST" });
  const { mutate: registerNicknameApi } = useMutationApi<{ user: User }, { nickname: string }>("/user/register", {
    method: "POST",
  });
  const { mutate: claimNicknameApi } = useMutationApi<{ user: User }, { nickname: string }>("/user/claim", {
    method: "POST",
  });

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await fetchMe();
      setUser(data.user);
    } finally {
      setLoading(false);
    }
  };

  const initSession = async () => {
    setLoading(true);
    try {
      const data = await initSessionApi({});
      setClientId(data.client_id);
      Cookies.set("client_id", data.client_id, { expires: 365 });
      await refresh();
    } finally {
      setLoading(false);
    }
  };

  const registerNickname = async (nickname: string) => {
    await registerNicknameApi({ nickname });
    await refresh();
  };

  const claimNickname = async (nickname: string) => {
    await claimNicknameApi({ nickname });
    await refresh();
  };

  useEffect(() => {
    void initSession();
  }, []);

  return (
    <AuthContext.Provider value={{ user, clientId, loading, registerNickname, claimNickname, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}
