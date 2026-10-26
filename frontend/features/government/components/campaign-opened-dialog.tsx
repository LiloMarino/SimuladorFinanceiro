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
import type { ElectionPanel, GovernmentNotice } from "@/types";
import type { ElectionShortcut } from "../lib/election";

type CampaignOpenedDialogProps = {
  /** O aviso da abertura, com as datas; nulo mantém o diálogo fechado */
  notice: GovernmentNotice | null;
  /** Dados atuais da eleição: dizem se quem vê já tem partido */
  panel: ElectionPanel | undefined;
  onClose: () => void;
  onShortcut: (shortcut: ElectionShortcut) => void;
};

/** A campanha abriu, para todos: as datas que importam e os atalhos para agir nela. */
export function CampaignOpenedDialog({ notice, panel, onClose, onShortcut }: CampaignOpenedDialogProps) {
  const hasParty = !!panel?.my_party;
  const canChoose = !hasParty && (panel?.can_found_or_join ?? false);
  const hasOpenParties = panel?.parties.some((party) => !party.is_computer) ?? false;

  return (
    <Dialog open={notice !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-130">
        {notice && (
          <>
            <DialogHeader variant="divided">
              <DialogTitle>A campanha eleitoral abriu</DialogTitle>
              <DialogDescription>A partida está pausada; retome pelo controle de velocidade no topo.</DialogDescription>
            </DialogHeader>

            <DialogBody>
              <Alert variant="info">
                <Flag />
                <AlertTitle>
                  1º turno em {notice.first_round ? displayShortDate(notice.first_round) : "data a definir"}
                </AlertTitle>
                <AlertDescription>
                  {notice.ticket_deadline && `As chapas fecham em ${displayShortDate(notice.ticket_deadline)}. `}
                  Até lá dá para fundar um partido, filiar-se a um e escolher quanto contribuir por mês: a contribuição
                  mensal compra votos para o partido, e quem começa cedo acumula mais.
                </AlertDescription>
              </Alert>
            </DialogBody>

            <DialogFooter variant="divided" className="sm:justify-end">
              <Button variant="outline" onClick={onClose}>
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
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
