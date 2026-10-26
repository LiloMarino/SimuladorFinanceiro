import { useState } from "react";
import { Info } from "lucide-react";
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
import { KeyValueRow } from "@/shared/components/key-value-row";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayMoneyWhole } from "@/shared/lib/utils/display";
import type { ElectionParty } from "@/types";
import { useJoinParty } from "../hooks/mutations/useJoinParty";
import { contributionAmount } from "../lib/contribution";
import { ContributionField } from "./contribution-field";
import { PartyMark } from "./party-mark";

type JoinPartyDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Os partidos de jogadores: o do computador não aceita filiação */
  parties: ElectionParty[];
  initialPartyId?: number | undefined;
  cash: string | undefined;
};

/** Filiar-se: escolhe o partido e quanto contribui por mês, que pode ser zero. */
export function JoinPartyDialog({ open, onOpenChange, parties, initialPartyId, cash }: JoinPartyDialogProps) {
  const [partyId, setPartyId] = useState(initialPartyId ?? parties[0]?.id);
  const [contribution, setContribution] = useState("");
  const join = useJoinParty(partyId ?? 0);

  const party = parties.find((candidate) => candidate.id === partyId);
  const monthly = Number(contributionAmount(contribution));
  const overCash = cash !== undefined && monthly > Number(cash);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Filiar-se a um partido</DialogTitle>
          <DialogDescription>Um partido por vez; sair é livre.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <div role="radiogroup" aria-label="Partido" className="grid gap-2">
              {parties.map((candidate) => {
                const selected = candidate.id === partyId;
                return (
                  <button
                    key={candidate.id}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    onClick={() => setPartyId(candidate.id)}
                    className={cn(
                      "grid grid-cols-[auto_1fr] items-center gap-x-2.5 gap-y-1 rounded-[10px] border px-3 py-2.5 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                      selected && "border-2 border-primary",
                    )}
                  >
                    <PartyMark abbr={candidate.abbr} color={candidate.color} size="md" />
                    <b className="text-[13px]">{candidate.name}</b>
                    <span />
                    <span className="text-xs text-muted-foreground">
                      Fundado por {candidate.founder} · {candidate.members.length}{" "}
                      {candidate.members.length === 1 ? "filiado" : "filiados"} · {displayMoneyWhole(candidate.budget)}
                      /mês · promessa {candidate.promise}
                    </span>
                  </button>
                );
              })}
            </div>

            {party && (
              <>
                <ContributionField
                  id="join-contribution"
                  value={contribution}
                  onChange={setContribution}
                  error={overCash ? `Seu caixa hoje é ${displayMoney(cash)}.` : null}
                  note={`Pode ser zero; dá para mudar todo mês. Com ${displayMoney(monthly)}, a verba do ${party.abbr} vai a ${displayMoneyWhole(Number(party.budget) + monthly)}/mês.`}
                />

                <div className="rounded-lg border px-3 py-1">
                  <KeyValueRow label="Quem escolhe a chapa" value={`${party.founder}, quem fundou`} />
                  <KeyValueRow label="Ranking de partidos" value={`seu patrimônio soma no ${party.abbr}`} />
                </div>
              </>
            )}

            <Alert variant="muted">
              <Info />
              <AlertTitle>Sair é livre</AlertTitle>
              <AlertDescription>
                A contribuição para na hora, e o que você já contribuiu não volta. Para entrar em outro partido, saia
                deste primeiro.
              </AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            disabled={!party || join.isPending}
            onClick={() =>
              join.mutate({ contribution: contributionAmount(contribution) }, { onSuccess: () => onOpenChange(false) })
            }
          >
            Filiar-se{party ? ` ao ${party.abbr}` : ""}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
