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
import { displayMoney } from "@/shared/lib/utils/display";
import type { ElectionParty } from "@/types";
import { useSetContribution } from "../hooks/mutations/useSetContribution";
import { contributionAmount, contributionText } from "../lib/contribution";
import { ContributionField } from "./contribution-field";

type ContributionDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  party: ElectionParty;
  /** Quanto o jogador contribui hoje, em reais */
  current: string;
  cash: string | undefined;
};

/** Mudar a contribuição mensal; vale a partir do próximo dia 1º. */
export function ContributionDialog({ open, onOpenChange, party, current, cash }: ContributionDialogProps) {
  const [text, setText] = useState(() => contributionText(current));
  const set = useSetContribution();
  const monthly = Number(contributionAmount(text));
  const overCash = cash !== undefined && monthly > Number(cash);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-110">
        <DialogHeader variant="divided">
          <DialogTitle>Contribuição ao {party.abbr}</DialogTitle>
          <DialogDescription>Vale a partir do próximo dia 1º; pode ser zero.</DialogDescription>
        </DialogHeader>
        <DialogBody>
          <ContributionField
            id="change-contribution"
            value={text}
            onChange={setText}
            error={overCash ? `Seu caixa hoje é ${displayMoney(cash)}.` : null}
            note={`Hoje você contribui com ${displayMoney(current)} por mês.`}
          />
        </DialogBody>
        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            disabled={set.isPending}
            onClick={() => set.mutate({ contribution: contributionAmount(text) }, { onSuccess: () => onOpenChange(false) })}
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
