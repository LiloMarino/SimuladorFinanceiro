import { useState } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { useAuth } from "@/shared/hooks/useAuth";
import type ApiError from "@/shared/lib/models/ApiError";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** Excluir a conta: o botão do diálogo só libera com o nickname digitado igual. */
export function DangerZoneCard({ nickname }: { nickname: string }) {
  const { deleteAccount, loading } = useAuth();
  const [confirming, setConfirming] = useState(false);
  const [typed, setTyped] = useState("");

  const open = (next: boolean) => {
    setConfirming(next);
    setTyped("");
  };

  const remove = async () => {
    try {
      await deleteAccount();
    } catch (err) {
      toastApiError(err as ApiError);
    }
  };

  return (
    <Card variant="destructive">
      <CardHeader>
        <CardTitle>Zona de perigo</CardTitle>
        <CardDescription>Não dá pra desfazer.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between gap-3">
          <div className="grid">
            <span className="font-semibold">Excluir conta</span>
            <span className="text-xs text-muted-foreground">Apaga seu nickname e seu histórico nas partidas.</span>
          </div>
          <Button variant="destructive" size="sm" onClick={() => open(true)}>
            Excluir conta
          </Button>
        </div>
      </CardContent>

      <AlertDialog open={confirming} onOpenChange={open}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir a conta {nickname}?</AlertDialogTitle>
            <AlertDialogDescription>
              Seu nickname e seu histórico somem de todas as partidas. Isso não pode ser desfeito.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Field>
            <FieldLabel htmlFor="confirm-nickname">
              Digite <b className="font-mono">{nickname}</b> pra confirmar
            </FieldLabel>
            <Input
              id="confirm-nickname"
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              autoComplete="off"
              autoFocus
            />
          </Field>
          <AlertDialogFooter>
            <AlertDialogCancel variant="outline">Cancelar</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              onClick={() => void remove()}
              disabled={typed !== nickname || loading}
            >
              Excluir conta
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
