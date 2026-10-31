import { useState } from "react";
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
import type { ElectionPanel, ElectionParty, VoterValue } from "@/types";
import { useSetPartyFlags } from "../hooks/mutations/useSetPartyFlags";
import { FLAGS_PER_PARTY } from "@/shared/lib/party-flags";
import { partyColor } from "@/shared/lib/party-colors";
import { FlagsPicker } from "./flags-picker";

type ChooseFlagsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  party: ElectionParty;
};

/** O fundador de um partido sem bandeiras escolhe as 3; depois elas não mudam mais. */
export function ChooseFlagsDialog({ open, onOpenChange, panel, party }: ChooseFlagsDialogProps) {
  const [flags, setFlags] = useState<VoterValue[]>([]);
  const [tried, setTried] = useState(false);
  const save = useSetPartyFlags();
  const missing = flags.length < FLAGS_PER_PARTY;

  const submit = () => {
    setTried(true);
    if (missing) return;
    save.mutate({ flags }, { onSuccess: () => onOpenChange(false) });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-230">
        <DialogHeader variant="divided">
          <DialogTitle>Escolha as bandeiras do {party.abbr}</DialogTitle>
          <DialogDescription>
            Até a escolha, o {party.abbr} entra na pesquisa com o perfil neutro e a mesma afinidade com todos os grupos.
            Depois de escolhidas, as bandeiras não mudam.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <FlagsPicker
            panel={panel}
            value={flags}
            onChange={setFlags}
            color={partyColor(party)}
            error={tried && missing ? `Escolha mais uma bandeira: o partido precisa de ${FLAGS_PER_PARTY}.` : undefined}
          />
        </DialogBody>
        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button disabled={save.isPending} onClick={submit}>
            Salvar as bandeiras
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
