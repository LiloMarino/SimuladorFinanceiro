import { useCallback, useEffect, type PropsWithChildren } from "react";
import { AuthContext } from "./AuthContext";
import { useSession } from "@/shared/hooks/queries/useSession";
import { useDeleteAccount } from "@/shared/hooks/mutations/useDeleteAccount";
import { useInitSession } from "@/shared/hooks/mutations/useInitSession";
import { useLogout } from "@/shared/hooks/mutations/useLogout";

export function AuthProvider({ children }: PropsWithChildren) {
  const { mutateAsync: initSession, isPending: initLoading } = useInitSession();

  const { data: session, error: sessionError, isLoading: sessionLoading } = useSession();

  const { mutateAsync: logoutApi, isPending: logoutLoading } = useLogout();
  const { mutateAsync: deleteAccountApi, isPending: deleteLoading } = useDeleteAccount();

  // Inicializa sessão apenas uma vez na montagem
  useEffect(() => {
    void initSession();
  }, [initSession]);

  const logout = useCallback(async () => {
    await logoutApi();

    // Garante novo client_id após logout
    await initSession();
  }, [initSession, logoutApi]);

  const deleteAccount = useCallback(async () => {
    await deleteAccountApi();

    // Garante novo client_id após exclusão
    await initSession();
  }, [initSession, deleteAccountApi]);

  return (
    <AuthContext.Provider
      value={{
        session: session ?? null,
        user: session?.user ?? null,
        logout,
        deleteAccount,
        loading: sessionLoading || initLoading || logoutLoading || deleteLoading,
        entryError: sessionError?.status === 423 ? sessionError : null,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
