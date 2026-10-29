import { useState } from "react";
import { TriangleAlert } from "lucide-react";
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
import { cn } from "@/shared/lib/utils";
import type { ElectionPanel, ElectionParty, RunoffRace } from "@/types";
import { useEndorse } from "../hooks/mutations/useEndorse";
import { followTotal } from "../lib/runoff";
import { PartyMark, PersonMark } from "./party-mark";

type EndorseDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  race: RunoffRace;
  party: ElectionParty;
};

/** A declaração do partido eliminado: apoiar um finalista ou ficar neutro. Vale uma vez e não se desfaz. */
export function EndorseDialog({ open, onOpenChange, panel, race, party }: EndorseDialogProps) {
  const finalists = race.finalists
    .map((id) => panel.parties.find((candidate) => candidate.id === id))
    .filter((candidate): candidate is ElectionParty => candidate !== undefined);
  // null é a neutralidade; o undefined é a escolha ainda não feita
  const [choice, setChoice] = useState<number | null | undefined>(undefined);
  const endorse = useEndorse();
  const transfer = race.transfers.find((item) => item.party_id === party.id);
  const weights = new Map(panel.groups.map((group) => [group.group, group.weight]));
  const follow = transfer ? followTotal(transfer, weights) : 0;
  const chosen = finalists.find((candidate) => candidate.id === choice);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Declarar apoio no 2º turno</DialogTitle>
          <DialogDescription>
            O {party.abbr} ficou de fora. Seus eleitores que hoje estão indecisos podem seguir a sua indicação.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <div role="radiogroup" aria-label="Apoio" className="grid gap-2.5">
              {finalists.map((finalist) => (
                <ChoiceButton
                  key={finalist.id}
                  selected={choice === finalist.id}
                  onSelect={() => setChoice(finalist.id)}
                  title={
                    <>
                      <b className="truncate font-medium">{finalist.candidate?.name ?? finalist.name}</b>
                      <PartyMark abbr={finalist.abbr} color={finalist.color} size="sm" />
                      {finalist.candidate && <PersonMark person={finalist.candidate} />}
                    </>
                  }
                  description={`Apoiar o ${finalist.abbr}: leva cerca de ${follow.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} pontos do eleitorado dos indecisos de hoje.`}
                />
              ))}
              <ChoiceButton
                selected={choice === null}
                onSelect={() => setChoice(null)}
                title={<b className="font-medium">Ficar neutro</b>}
                description="Ninguém é indicado: os indecisos continuam livres para a campanha dos finalistas."
              />
            </div>

            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>A declaração vale uma vez</AlertTitle>
              <AlertDescription>
                Quanto mais o grupo confia no {party.abbr}, mais indecisos seguem a indicação. A sala vê a declaração, e
                a neutralidade também é uma escolha definitiva.
              </AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            disabled={choice === undefined || endorse.isPending}
            onClick={() =>
              choice !== undefined && endorse.mutate({ party_id: choice }, { onSuccess: () => onOpenChange(false) })
            }
          >
            {choice === null ? "Declarar neutralidade" : `Apoiar${chosen ? ` o ${chosen.abbr}` : ""}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

type ChoiceButtonProps = {
  selected: boolean;
  onSelect: () => void;
  title: React.ReactNode;
  description: string;
};

function ChoiceButton({ selected, onSelect, title, description }: ChoiceButtonProps) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      onClick={onSelect}
      className={cn(
        "grid gap-1 rounded-[10px] border px-3 py-2.5 text-left text-[13px] outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        selected && "border-2 border-primary",
      )}
    >
      <span className="flex min-w-0 items-center gap-1.5">{title}</span>
      <span className="text-xs text-muted-foreground">{description}</span>
    </button>
  );
}
