import { useState } from "react";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { Copy, Medal, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { BrandMark } from "@/shared/components/brand-mark";
import { useAchievementTally } from "@/shared/hooks/queries/useAchievementTally";
import { useTunnelStatus } from "../hooks/queries/useTunnelStatus";
import { useStartTunnel } from "../hooks/mutations/useStartTunnel";

type LobbyHeaderProps = {
  isHost: boolean;
  hostNickname: string;
};

/** Topo do lobby: de quem é a sala e o link para chamar os outros. */
export function LobbyHeader({ isHost, hostNickname }: LobbyHeaderProps) {
  const { data: tunnelStatus } = useTunnelStatus();
  const { mutate: startTunnel, isPending: tunnelLoading } = useStartTunnel();
  const [copyFailed, setCopyFailed] = useState(false);
  const tally = useAchievementTally();

  // O provider "lan" também responde como ativo, mas o link dele só vale na rede local
  const publicLink = tunnelStatus?.active && tunnelStatus.provider !== "lan" ? tunnelStatus.url : null;
  const shareableLink = tunnelStatus?.url ?? `http://${window.location.host}`;

  // O navegador só libera a área de transferência em https (ou localhost)
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareableLink);
      setCopyFailed(false);
      toast.success("Link copiado");
    } catch {
      setCopyFailed(true);
    }
  };

  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="flex items-center gap-3">
        <BrandMark />
        <div className="grid">
          <h1 className="text-xl font-bold">Sala {hostNickname ? `de ${hostNickname}` : ""}</h1>
          <span className="text-muted-foreground">
            {isHost ? "Aguardando você iniciar · você é o host" : `Aguardando ${hostNickname} iniciar`}
          </span>
        </div>
        {/* Conquistas */}
        <Button variant="outline" nativeButton={false} render={<Link to="/achievements" />} className="ml-2">
          <Medal />
          Conquistas
          {tally && (
            <span className="text-muted-foreground tabular-nums">
              {tally.unlocked}/{tally.total}
            </span>
          )}
          {tally?.hasNew && <span aria-label="Conquista nova" className="size-1.5 rounded-full bg-toast-warning" />}
        </Button>
      </div>

      {/* Convite */}
      <div className="flex min-w-[380px] flex-col gap-1.5">
        <span className="text-xs font-medium text-muted-foreground">
          Convide pelo link · {publicLink ? "internet" : "rede local"}
        </span>
        <div className="flex gap-1.5">
          <output className="flex h-10 flex-1 items-center rounded-lg border border-input bg-card px-3 font-mono text-[13px] select-all">
            {shareableLink}
          </output>
          <Button variant="dark" onClick={copyLink}>
            <Copy />
            Copiar
          </Button>
        </div>
        {copyFailed && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertDescription>
              O navegador só copia sozinho em https. Selecione o link e copie com Ctrl+C.
            </AlertDescription>
          </Alert>
        )}
        {isHost && tunnelStatus && !tunnelStatus.active && (
          <Button variant="link" size="sm" className="self-start" disabled={tunnelLoading} onClick={() => startTunnel()}>
            {tunnelLoading ? "Gerando link público…" : "Gerar link público pra quem está fora da rede →"}
          </Button>
        )}
      </div>
    </header>
  );
}
