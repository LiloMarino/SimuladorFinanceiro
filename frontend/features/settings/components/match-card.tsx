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
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { winRuleLabel } from "@/shared/lib/game-types";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** Só para o host: encerra a partida e leva todos ao resultado, que chega pelo evento de fim. */
export function MatchCard() {
  const [confirming, setConfirming] = useState(false);
  const { simulation } = useSimulation();
  const { data: players } = useRoomPlayers();

  const { mutate: stop, isPending } = useApiMutation({
    mutationFn: () => apiFetch("/api/simulation/stop", { method: "POST" }),
    onSuccess: () => setConfirming(false),
    onError: (err) => toastApiError(err),
  });

  const count = players?.length ?? 0;
  const match = simulation?.simulation;
  const criterion = match ? winRuleLabel(match.game_type, match.victory_criterion) : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Partida</CardTitle>
        <CardDescription>Só o host vê esta seção.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between gap-3">
          <div className="grid">
            <span className="font-semibold">Encerrar a partida agora</span>
            <span className="text-xs text-muted-foreground">
              Todos vão pra tela de resultado com o pódio. A partida fica salva.
            </span>
          </div>
          <Button variant="dark" size="sm" onClick={() => setConfirming(true)} disabled={isPending}>
            Encerrar partida
          </Button>
        </div>
      </CardContent>

      <AlertDialog open={confirming} onOpenChange={setConfirming}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Encerrar a partida {count > 1 ? `pros ${count} jogadores` : "agora"}?</AlertDialogTitle>
            <AlertDialogDescription>
              Todos vão direto pra tela de resultado{criterion && `, com o pódio por ${criterion}`}. A partida fica
              salva e pode ser comparada depois.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel variant="outline">Cancelar</AlertDialogCancel>
            <AlertDialogAction variant="dark" onClick={() => stop()} disabled={isPending}>
              Encerrar partida
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
