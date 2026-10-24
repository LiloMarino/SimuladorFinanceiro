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
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { cn } from "@/shared/lib/utils";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { ElectionPanel } from "@/types";
import { useDonate } from "../hooks/mutations/useDonate";
import { monthlyYield } from "../lib/election";
import { PartyMark, PersonMark } from "./party-mark";

type DonateDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  cash: string | undefined;
};

/** Doar a um finalista entre os turnos: a favor de quem lidera ou contra. */
export function DonateDialog({ open, onOpenChange, panel, cash }: DonateDialogProps) {
  const finalists = panel.parties.filter((party) => panel.finalists.includes(party.id));
  const [partyId, setPartyId] = useState(finalists[0]?.id);
  const [text, setText] = useState("");
  const donate = useDonate();

  const amount = Number(normalizeNumberString(text)) || 0;
  const target = finalists.find((party) => party.id === partyId);
  const overCash = cash !== undefined && amount > Number(cash);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Doar a um finalista</DialogTitle>
          <DialogDescription>
            Quem ficou de fora escolhe o finalista, a favor de quem lidera ou contra. Até {displayDayMonth(panel.dates.donation_deadline)}.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <div role="radiogroup" aria-label="Finalista" className="grid gap-2">
              {finalists.map((party) => (
                <button
                  key={party.id}
                  type="button"
                  role="radio"
                  aria-checked={party.id === partyId}
                  onClick={() => setPartyId(party.id)}
                  className={cn(
                    "flex items-center gap-2.5 rounded-[10px] border px-3 py-2.5 text-left text-[13px] outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                    party.id === partyId && "border-2 border-primary",
                  )}
                >
                  <PartyMark abbr={party.abbr} color={party.color} />
                  {party.candidate && <PersonMark person={party.candidate} />}
                  <b className="flex-1 font-medium">{party.candidate?.name ?? party.name}</b>
                  <span className="font-mono text-xs text-muted-foreground">
                    promessa {party.promise}
                  </span>
                </button>
              ))}
            </div>

            <Field data-invalid={overCash}>
              <FieldLabel htmlFor="donation-amount">Valor da doação</FieldLabel>
              <Input
                id="donation-amount"
                fieldSize="xl"
                numeric
                inputMode="decimal"
                placeholder="R$ 0,00"
                value={text}
                aria-invalid={overCash}
                onChange={(event) => setText(formatMoney(event.target.value))}
              />
              {overCash ? (
                <FieldError>Seu caixa hoje é {displayMoney(cash)}.</FieldError>
              ) : (
                <FieldDescription>
                  {target && amount > 0
                    ? `${displayMoney(amount)} rendem +${monthlyYield(amount).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} ponto de intenção ao ${target.abbr}: a raiz do valor dividida por 64, como a verba de campanha.`
                    : "Sai do seu caixa de uma vez e vira apoio do finalista."}
                </FieldDescription>
              )}
            </Field>

            <Alert variant="muted">
              <Info />
              <AlertTitle>A sala vê a doação</AlertTitle>
              <AlertDescription>
                O aviso mostra quem doou, quanto e a quem, como uma doação de campanha declarada.
              </AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            disabled={!target || amount <= 0 || overCash || donate.isPending}
            onClick={() =>
              target &&
              donate.mutate(
                { party_id: target.id, amount: normalizeNumberString(text) },
                { onSuccess: () => onOpenChange(false) },
              )
            }
          >
            Doar{target ? ` ao ${target.abbr}` : ""}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
