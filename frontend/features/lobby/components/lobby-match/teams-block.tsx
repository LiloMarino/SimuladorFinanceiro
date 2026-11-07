import { Users } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import type { TeamsCheck } from "../../lib/teams-check";

type TeamsBlockProps = {
  teams: TeamsCheck;
  isHost: boolean;
  distributing: boolean;
  onDistribute: () => void;
};

/** Equipes: o que falta para iniciar e o atalho do host. */
export function TeamsBlock({ teams, isHost, distributing, onDistribute }: TeamsBlockProps) {
  return (
    <div className="grid gap-2">
      <span className="text-[13px] text-muted-foreground">
        {teams.missing.length > 0
          ? "Para iniciar, todo mundo precisa estar numa equipe"
          : "Todos na mesma equipe: não dá pra iniciar"}
      </span>
      {isHost && teams.missing.length > 0 && (
        <Button variant="outline" disabled={distributing} onClick={onDistribute}>
          {distributing ? <Spinner /> : <Users />}
          Distribuir quem falta
        </Button>
      )}
    </div>
  );
}
