import { Flag } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import type { ElectionShortcut } from "../lib/election";

type CampaignOpenedDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  onShortcut: (shortcut: ElectionShortcut) => void;
};

/** A campanha está aberta: as datas que importam e os atalhos para agir nela. */
export function CampaignOpenedDialog({ open, onOpenChange, panel, onShortcut }: CampaignOpenedDialogProps) {
  const hasParty = !!panel.my_party;
  const canChoose = !hasParty && panel.can_found_or_join;
  const hasOpenParties = panel.parties.some((party) => !party.is_computer);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>A campanha eleitoral abriu</DialogTitle>
          <DialogDescription>As datas da eleição e o que dá para fazer até lá.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <Alert variant="info">
            <Flag />
            <AlertTitle>1º turno em {displayShortDate(panel.dates.first_round)}</AlertTitle>
            <AlertDescription>
              As chapas fecham em {displayShortDate(panel.dates.ticket_deadline)}. Até lá dá para fundar um partido,
              filiar-se a um e escolher quanto contribuir por mês: a contribuição mensal compra votos para o partido, e
              quem começa cedo acumula mais.
            </AlertDescription>
          </Alert>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
          {hasParty && <Button onClick={() => onShortcut("contribution")}>Contribuição</Button>}
          {canChoose && hasOpenParties && (
            <Button variant="outline" onClick={() => onShortcut("join")}>
              Filiar-se
            </Button>
          )}
          {canChoose && <Button onClick={() => onShortcut("found")}>Fundar partido</Button>}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
