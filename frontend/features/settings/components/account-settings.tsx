import { useState } from "react";
import { useAuth } from "@/shared/hooks/useAuth";
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
  const { logout, deleteAccount, loading } = useAuth();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleLogout = async () => {
    await logout();
  };

  const handleDeleteAccount = async () => {
    try {
      await deleteAccount();
      toast.success("Conta excluída com sucesso!");
      setShowDeleteConfirm(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Erro ao excluir conta");
    }
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
            disabled={loading}
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
              <Button variant="destructive" onClick={handleDeleteAccount} disabled={loading}>
                Confirmar Exclusão
              </Button>
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
