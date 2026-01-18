import { useState } from "react";
import { useAuth } from "@/shared/hooks/useAuth";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogAction,
  AlertDialogCancel,
} from "@/shared/components/ui/alert-dialog";

export function AccountSettings() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { mutate: deleteAccount, loading: deletingAccount } = useMutationApi("/api/user", {
    method: "DELETE",
    onSuccess: () => {
      toast.success("Conta excluída com sucesso!");
      handleLogout();
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const handleDeleteAccount = () => {
    deleteAccount({});
    setShowDeleteConfirm(false);
  };

  return (
    <div className="max-w-sm space-y-4">
      {/* Sair da Conta - Ação direta sem confirmação */}
      <div>
        <Button onClick={handleLogout} variant="outline" className="w-full">
          Sair da Conta
        </Button>
        <p className="text-xs text-gray-500 mt-2">Você será desconectado do simulador.</p>
      </div>

      {/* Excluir Conta - Com AlertDialog para confirmação */}
      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <div>
          <Button
            onClick={() => setShowDeleteConfirm(true)}
            variant="destructive"
            className="w-full"
            disabled={deletingAccount}
          >
            Excluir Conta
          </Button>
          <p className="text-xs text-gray-500 mt-2">Esta ação é permanente e não pode ser desfeita.</p>
        </div>

        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir Conta</AlertDialogTitle>
            <AlertDialogDescription>
              ⚠️ Esta ação é irreversível! Todos os seus dados serão perdidos.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <AlertDialogFooter>
            <AlertDialogCancel asChild>
              <Button variant="outline">Cancelar</Button>
            </AlertDialogCancel>
            <AlertDialogAction asChild>
              <Button variant="destructive" onClick={handleDeleteAccount} disabled={deletingAccount}>
                Confirmar Exclusão
              </Button>
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
