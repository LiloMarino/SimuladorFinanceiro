import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import { useAuth } from "@/shared/hooks/useAuth";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";

/** Barra do topo das telas fora da partida: volta ao lobby, sala e jogador. */
export function PlainTopbar() {
  const { session } = useAuth();
  const { data: settings } = useSimulationSettings();
  const nickname = session?.user?.nickname;

  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex w-full max-w-[1120px] items-center justify-between gap-4 px-7 py-3">
        <Button variant="link" size="sm" nativeButton={false} render={<Link to="/lobby" />}>
          <ArrowLeft />
          Voltar ao lobby
        </Button>
        <div className="flex items-center gap-2.5">
          {settings && <span className="text-muted-foreground">Sala de {settings.host_nickname}</span>}
          {nickname && (
            <PlayerAvatar
              nickname={nickname}
              color={settings?.selected_players.find((p) => p.nickname === nickname)?.color}
            />
          )}
        </div>
      </div>
    </header>
  );
}
