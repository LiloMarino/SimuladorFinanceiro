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
import { displayDayMonth, displayMoney, displayMoneyCompact, displayPercent } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { ElectionPanel } from "@/types";
import { useDonate } from "../hooks/mutations/useDonate";
import { useToday } from "../hooks/useToday";
import { countdownLabel, monthlyYield } from "../lib/election";
import { contributionText } from "../lib/contribution";
import { PartyMark, PersonMark } from "./party-mark";

type DonateDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  cash: string | undefined;
};

const SHORTCUTS = [5000, 10000, 20000];

/** Doar a um finalista entre os turnos: a favor de quem lidera ou contra. */
export function DonateDialog({ open, onOpenChange, panel, cash }: DonateDialogProps) {
  const finalists = panel.parties.filter((party) => panel.finalists.includes(party.id));
  const [partyId, setPartyId] = useState(finalists[0]?.id);
  const [text, setText] = useState("");
  const donate = useDonate();
  const mine = panel.my_party ? panel.parties.find((party) => party.id === panel.my_party?.party_id) : undefined;
  const simulation = panel.runoff_simulation;
  const today = useToday(panel);

  const amount = Number(normalizeNumberString(text)) || 0;
  const target = finalists.find((party) => party.id === partyId);
  const overCash = cash !== undefined && amount > Number(cash);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Doar a um finalista</DialogTitle>
          <DialogDescription>
            Entre os turnos, até {displayDayMonth(panel.dates.donation_deadline)}.
            {mine && ` Você é do ${mine.abbr}${panel.finalists.includes(mine.id) ? "." : ", que ficou de fora."}`}
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <div role="radiogroup" aria-label="Finalista" className="grid grid-cols-2 gap-2.5">
              {finalists.map((party) => {
                const entry = simulation?.entries.find((candidate) => candidate.party_id === party.id);
                const leads = simulation?.winner === party.id;
                return (
                  <button
                    key={party.id}
                    type="button"
                    role="radio"
                    aria-checked={party.id === partyId}
                    onClick={() => setPartyId(party.id)}
                    className={cn(
                      "grid gap-1 rounded-[10px] border px-3 py-2.5 text-left text-[13px] outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                      party.id === partyId && "border-2 border-primary",
                    )}
                  >
                    <span className="flex min-w-0 items-center gap-1.5">
                      <b className="truncate font-medium">{party.candidate?.name ?? party.name}</b>
                      <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                      {party.candidate && <PersonMark person={party.candidate} />}
                    </span>
                    {entry && (
                      <span className="text-xs text-muted-foreground">
                        {displayPercent(entry.share, 0)} na simulação ·{" "}
                        {leads ? "lidera" : "doar aqui é contra quem lidera"}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            <Field data-invalid={overCash}>
              <FieldLabel htmlFor="donation-amount">Quanto</FieldLabel>
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
              <div className="flex flex-wrap gap-1.5">
                {SHORTCUTS.map((shortcut) => (
                  <Button
                    key={shortcut}
                    type="button"
                    size="xs"
                    variant={amount === shortcut ? "info" : "outline"}
                    onClick={() => setText(contributionText(String(shortcut)))}
                  >
                    {displayMoneyCompact(shortcut)}
                  </Button>
                ))}
              </div>
              {overCash ? (
                <FieldError>Seu caixa hoje é {displayMoney(cash)}.</FieldError>
              ) : (
                <FieldDescription>
                  Sai do seu caixa de uma vez e vira verba do {target?.abbr ?? "finalista"} nos{" "}
                  {countdownLabel(today, panel.dates.runoff)} até o 2º turno.
                </FieldDescription>
              )}
            </Field>

            {target && amount > 0 && (
              <dl className="grid divide-y rounded-lg border px-3 text-[13px]">
                <div className="flex justify-between gap-3 py-1.5">
                  <dt className="text-muted-foreground">Efeito estimado</dt>
                  <dd className="text-right font-mono font-semibold">
                    +{monthlyYield(amount).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} pontos para o{" "}
                    {target.abbr}
                  </dd>
                </div>
                <div className="flex justify-between gap-3 py-1.5">
                  <dt className="text-muted-foreground">Seu patrimônio no ranking</dt>
                  <dd className="text-right font-mono font-semibold">−{displayMoney(amount)}</dd>
                </div>
                {mine && (
                  <div className="flex justify-between gap-3 py-1.5">
                    <dt className="text-muted-foreground">{mine.abbr} no ranking de partidos</dt>
                    <dd className="text-right font-mono font-semibold">−{displayMoney(amount)}</dd>
                  </div>
                )}
              </dl>
            )}

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
