import { useState } from "react";
import { Flag } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { useAuth } from "@/shared/hooks/useAuth";
import type { SimulationSettings } from "@/types";
import { useMyPreparation } from "../../hooks/queries/useMyPreparation";
import { usePreparations } from "../../hooks/queries/usePreparations";
import { partyOf } from "../../lib/preparation";
import { PreparationDialog } from "./preparation-dialog";

type PreparationButtonProps = {
  rules: SimulationSettings["simulation"];
  selectedSimulationId: SimulationSettings["selected_simulation_id"];
};

/** "Minha preparação" no cabeçalho do lobby: diz o partido preparado e conta o convite de vice sem resposta. */
export function PreparationButton({ rules, selectedSimulationId }: PreparationButtonProps) {
  const [open, setOpen] = useState(false);
  const { data: preparations } = usePreparations();
  const { data: mine } = useMyPreparation();
  const { user } = useAuth();
  const party = preparations && user ? partyOf(preparations, user.nickname) : null;
  const invited = mine?.invite && !preparations?.locked_reason;

  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}>
        <Flag />
        Minha preparação
        {party && (
          <span className="inline-flex items-center gap-1">
            {party.founder !== user?.nickname && <span className="text-xs text-muted-foreground">no</span>}
            <PartyMark abbr={party.party.abbr} color={party.party.color} size="sm" />
          </span>
        )}
        {invited && (
          <Badge variant="count" size="count" aria-label="1 convite de vice esperando resposta">
            1
          </Badge>
        )}
      </Button>
      <PreparationDialog open={open} onOpenChange={setOpen} rules={rules} selectedSimulationId={selectedSimulationId} />
    </>
  );
}
