import { LogOut } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";

/** Como você aparece pra sala, e a saída da conta. */
export function ProfileCard({ nickname }: { nickname: string }) {
  const { logout, loading } = useAuth();
  const { data: players } = useRoomPlayers();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Perfil</CardTitle>
        <CardDescription>Como você aparece pra sala.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid justify-items-start gap-3.5">
          <div className="flex items-center gap-3">
            <PlayerAvatar nickname={nickname} color={players?.find((p) => p.nickname === nickname)?.color} size="xl" />
            <div className="grid">
              <span className="text-base font-semibold">{nickname}</span>
              <span className="text-xs text-muted-foreground">O nickname não muda depois de criado.</span>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={() => void logout()} disabled={loading}>
            <LogOut />
            Sair da conta
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
