import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ErrorState } from "@/shared/components/error-state";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { simulationSettingsOptions } from "@/shared/lib/queries/simulationSettingsOptions";
import { LoadingPage } from "@/pages/loading";
import type { SimulationSettings } from "@/types";
import { LobbyHeader } from "../components/lobby-header";
import { LobbyMatch } from "../components/lobby-match";
import { LobbyPlayersList } from "../components/lobby-player-list";
import { OfflineTools } from "../components/offline-tools";
import { SavedSimulationsDialog } from "../components/saved-simulations-dialog";

export function LobbyPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { logout } = useAuth();
  const { data: settings, isLoading, error, refetch } = useQuery(simulationSettingsOptions());

  useRealtime("simulation_started", (simulation) => {
    if (simulation.active) {
      navigate("/", { replace: true });
    }
  });

  // A partida selecionada pelo host muda as cores da sala e quem está travado
  useRealtime("simulation_selected", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.simulationSettings() });
  });

  if (isLoading) {
    return <LoadingPage variant="fullscreen" />;
  }

  if (!settings) {
    return (
      <section className="flex min-h-svh items-center justify-center p-6">
        <Card className="w-full max-w-105">
          <CardContent>
            <ErrorState
              title="Não deu pra entrar na sala"
              description="O servidor do host não respondeu. Confira se ele está ligado e na mesma rede."
              error={error}
              onRetry={() => void refetch()}
            >
              <Button variant="outline" onClick={() => void logout()}>
                Sair
              </Button>
            </ErrorState>
          </CardContent>
        </Card>
      </section>
    );
  }

  return <LobbyContent settings={settings} />;
}

function LobbyContent({ settings }: { settings: SimulationSettings }) {
  const [savedOpen, setSavedOpen] = useState(false);

  return (
    <div className="mx-auto flex max-w-280 flex-col gap-5 px-7 py-10">
      <LobbyHeader isHost={settings.is_host} hostNickname={settings.host_nickname} />

      <div className="grid items-start gap-5 lg:grid-cols-[1.25fr_1fr]">
        <LobbyPlayersList
          hostNickname={settings.host_nickname}
          savedPlayers={settings.selected_players}
          selectedSimulationId={settings.selected_simulation_id}
        />
        <LobbyMatch
          simulationData={settings.simulation}
          isHost={settings.is_host}
          hostNickname={settings.host_nickname}
          selectedSimulationId={settings.selected_simulation_id}
          savedPlayers={settings.selected_players}
          onOpenSaved={() => setSavedOpen(true)}
        />
      </div>

      <OfflineTools onOpenSaved={() => setSavedOpen(true)} />

      <SavedSimulationsDialog
        open={savedOpen}
        onOpenChange={setSavedOpen}
        isHost={settings.is_host}
        selectedSimulationId={settings.selected_simulation_id}
      />
    </div>
  );
}
