import { useState } from "react";
import { Flag } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { PROFESSIONS } from "@/shared/lib/professions";
import type { SimulationSettings } from "@/types";
import { useMyPreparation } from "../../hooks/queries/useMyPreparation";
import { usePreparations } from "../../hooks/queries/usePreparations";
import { partyOf } from "../../lib/preparation";
import { PreparationDialog } from "./preparation-dialog";

type PreparationButtonProps = {
  rules: SimulationSettings["simulation"];
  selectedSimulationId: SimulationSettings["selected_simulation_id"];
  professions: boolean;
  savedPlayers: SimulationSettings["selected_players"];
};

/** "Minha preparação" no cabeçalho do lobby: diz a profissão e o partido preparados e conta os convites de vice sem resposta. */
export function PreparationButton({ rules, selectedSimulationId, professions, savedPlayers }: PreparationButtonProps) {
  const [open, setOpen] = useState(false);
  const { data: preparations } = usePreparations();
  const { data: mine } = useMyPreparation();
  const { data: players } = useRoomPlayers();
  const { user } = useAuth();
  const party = preparations && user ? partyOf(preparations, user.nickname) : null;
  const invites = preparations?.locked_reason ? 0 : (mine?.invites.length ?? 0);
  const profession = professions ? players?.find((player) => player.nickname === user?.nickname)?.profession : null;

  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        <Flag />
        Minha preparação
        {profession && <span className="text-xs text-muted-foreground">{PROFESSIONS[profession].name}</span>}
        {party && (
          <span className="inline-flex items-center gap-1">
            {party.founder !== user?.nickname && <span className="text-xs text-muted-foreground">no</span>}
            <PartyMark abbr={party.party.abbr} color={party.party.color} size="sm" />
          </span>
        )}
        {invites > 0 && (
          <Badge variant="count" size="count" aria-label={`${invites} convite(s) de vice esperando resposta`}>
            {invites}
          </Badge>
        )}
      </Button>
      <PreparationDialog
        open={open}
        onOpenChange={setOpen}
        rules={rules}
        selectedSimulationId={selectedSimulationId}
        professions={professions}
        savedPlayers={savedPlayers}
      />
    </>
  );
}
