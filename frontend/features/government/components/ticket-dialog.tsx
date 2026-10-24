import { useState } from "react";
import { Info, TriangleAlert } from "lucide-react";
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
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { useSetTicket } from "../hooks/mutations/useSetTicket";
import { remainingCollections } from "../lib/election";

const NO_VICE = "none";

type TicketDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  party: ElectionParty;
  panel: ElectionPanel;
  cash: string | undefined;
};

/** Montar a chapa: candidato e vice entre os filiados, com a conta da campanha até o 1º turno. */
export function TicketDialog({ open, onOpenChange, party, panel, cash }: TicketDialogProps) {
  const [candidate, setCandidate] = useState(party.candidate?.nickname ?? party.members[0]?.nickname ?? "");
  const [vice, setVice] = useState(party.vice?.nickname ?? NO_VICE);
  const setTicket = useSetTicket();

  const nicknames = Object.fromEntries(party.members.map((member) => [member.nickname, member.nickname]));
  const viceItems = { [NO_VICE]: "Sem vice", ...Object.fromEntries(party.members.filter((m) => m.nickname !== candidate).map((m) => [m.nickname, m.nickname])) };
  const effectiveVice = vice === candidate ? NO_VICE : vice;

  const collections = remainingCollections(panel.today, panel.dates.first_round);
  const myMonthly = Number(panel.my_party?.contribution ?? 0);
  const myShare = myMonthly * collections;
  const overCash = cash !== undefined && myShare > Number(cash);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Montar a chapa do {party.abbr}</DialogTitle>
          <DialogDescription>
            Só quem fundou monta a chapa. Inscrições até {displayDayMonth(panel.dates.ticket_deadline)}.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <Field>
              <FieldLabel>Candidato</FieldLabel>
              <Select
                value={candidate}
                items={nicknames}
                onValueChange={(value) => value && setCandidate(value)}
              >
                <SelectTrigger className="w-full" aria-label="Candidato">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {party.members.map((member) => (
                    <SelectItem key={member.nickname} value={member.nickname}>
                      {member.nickname}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FieldDescription>Entre os filiados.</FieldDescription>
            </Field>

            <Field>
              <FieldLabel>Vice</FieldLabel>
              <Select
                value={effectiveVice}
                items={viceItems}
                onValueChange={(value) => value && setVice(value)}
              >
                <SelectTrigger className="w-full" aria-label="Vice">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NO_VICE}>Sem vice</SelectItem>
                  {party.members
                    .filter((member) => member.nickname !== candidate)
                    .map((member) => (
                      <SelectItem key={member.nickname} value={member.nickname}>
                        {member.nickname}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              <FieldDescription>
                {effectiveVice === NO_VICE
                  ? "Sem vice, a chapa concorre só com o candidato."
                  : `${effectiveVice} recebe o convite e aceita ou recusa. Até lá, a chapa concorre sem vice.`}
              </FieldDescription>
            </Field>

            <div className="rounded-lg border px-3 py-1">
              <KeyValueRow label="Verba do partido" value={`${displayMoney(party.budget)}/mês`} />
              <KeyValueRow
                label={`Até o 1º turno (${collections} ${collections === 1 ? "mês" : "meses"})`}
                value={displayMoney(Number(party.budget) * collections)}
              />
              <KeyValueRow label="Sua parte até o 1º turno" value={displayMoney(myShare)} />
              {cash !== undefined && <KeyValueRow label="Seu caixa hoje" value={displayMoney(cash)} />}
            </div>

            {overCash && (
              <Alert variant="warning">
                <TriangleAlert />
                <AlertTitle>Seu caixa não cobre a sua parte inteira</AlertTitle>
                <AlertDescription>
                  Mês sem caixa pula a sua contribuição, e a verba do partido cai junto. O que você contribui sai do seu
                  patrimônio.
                </AlertDescription>
              </Alert>
            )}
            <Alert variant="muted">
              <Info />
              <AlertTitle>A sala vê o partido inteiro</AlertTitle>
              <AlertDescription>Chapa, filiados, contribuições e promessa são públicos desde o primeiro dia.</AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            disabled={!candidate || setTicket.isPending}
            onClick={() =>
              setTicket.mutate(
                { candidate, vice: effectiveVice === NO_VICE ? null : effectiveVice },
                { onSuccess: () => onOpenChange(false) },
              )
            }
          >
            Inscrever a chapa
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
