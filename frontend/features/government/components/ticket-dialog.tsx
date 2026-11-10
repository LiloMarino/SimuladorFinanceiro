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
import { PlayerOption } from "@/shared/components/player-option";
import { DisabledHint } from "@/shared/components/disabled-hint";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { useInviteVice } from "../hooks/mutations/useInviteVice";
import { useSetTicket } from "../hooks/mutations/useSetTicket";
import { useWithdrawVice } from "../hooks/mutations/useWithdrawVice";
import { remainingCollections } from "../lib/election";

type TicketDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  party: ElectionParty;
  panel: ElectionPanel;
  cash: string | undefined;
};

/** Montar a chapa: candidato entre os filiados e, à parte, o convite ao vice entre os jogadores da sala, com a conta da campanha até o 1º turno. */
export function TicketDialog({ open, onOpenChange, party, panel, cash }: TicketDialogProps) {
  const [candidate, setCandidate] = useState(party.candidate?.nickname ?? party.members[0]?.nickname ?? "");
  const [vice, setVice] = useState<string | null>(party.vice?.nickname ?? null);
  const setTicket = useSetTicket();
  const inviteVice = useInviteVice();
  const withdrawVice = useWithdrawVice();

  const candidateItems = Object.fromEntries(
    party.members.map((member) => [
      member.nickname,
      <PlayerOption key={member.nickname} nickname={member.nickname} color={member.color} />,
    ]),
  );
  const blockedBy = Object.fromEntries(panel.vice_options.map((option) => [option.nickname, option.blocked]));
  const viceOptions = panel.vice_options.filter((option) => option.nickname !== candidate);
  const viceItems = Object.fromEntries(
    viceOptions.map((option) => [
      option.nickname,
      <PlayerOption key={option.nickname} nickname={option.nickname} color={option.color} />,
    ]),
  );
  const chosenVice = vice === candidate ? null : vice;
  // O convite vigente da chapa, que o botão Convidar substitui
  const invitedNickname = party.vice?.nickname ?? null;
  const sameAsInvited = chosenVice !== null && chosenVice === invitedNickname && party.vice_phase !== "DECLINED";

  const collections = remainingCollections(panel.today, panel.dates.first_round);
  const myMonthly = Number(panel.my_party?.contribution ?? 0);
  const myShare = myMonthly * collections;
  const overCash = cash !== undefined && myShare > Number(cash);

  // O motivo do botão apagado: o que falta para inscrever a chapa
  const blockedReason = !candidate && !setTicket.isPending ? "Escolha um candidato." : null;
  const inviteReason =
    chosenVice === null ? "Escolha o vice." : sameAsInvited ? "Esse jogador já foi convidado." : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Montar a chapa do {party.abbr}</DialogTitle>
          <DialogDescription>
            Só quem fundou monta a chapa. Inscrever a chapa não convida o vice. Inscrições até{" "}
            {displayDayMonth(panel.dates.ticket_deadline)}.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <Field>
              <FieldLabel>Candidato</FieldLabel>
              <Select value={candidate} items={candidateItems} onValueChange={(value) => value && setCandidate(value)}>
                <SelectTrigger className="w-full" aria-label="Candidato">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {party.members.map((member) => (
                    <SelectItem key={member.nickname} value={member.nickname} disabled={!!blockedBy[member.nickname]}>
                      <PlayerOption nickname={member.nickname} color={member.color} />
                      {blockedBy[member.nickname] && (
                        <span className="text-xs text-muted-foreground">{blockedBy[member.nickname]}</span>
                      )}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FieldDescription>Entre os filiados.</FieldDescription>
            </Field>

            <Field>
              <FieldLabel>Vice</FieldLabel>
              <div className="flex gap-2">
                <Select value={chosenVice} items={viceItems} onValueChange={(value) => value && setVice(value)}>
                  <SelectTrigger className="w-full" aria-label="Vice">
                    <SelectValue placeholder="Escolha o vice" />
                  </SelectTrigger>
                  <SelectContent>
                    {viceOptions.map((option) => (
                      <SelectItem key={option.nickname} value={option.nickname} disabled={!!option.blocked}>
                        <PlayerOption nickname={option.nickname} color={option.color} />
                        <span className="text-xs text-muted-foreground">
                          {option.blocked ?? (option.party_abbr ? `do ${option.party_abbr}` : "sem partido")}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <DisabledHint reason={inviteReason}>
                  <Button
                    variant="outline"
                    disabled={chosenVice === null || sameAsInvited || inviteVice.isPending}
                    onClick={() => chosenVice && inviteVice.mutate({ vice: chosenVice })}
                  >
                    Convidar
                  </Button>
                </DisabledHint>
              </div>
              <FieldDescription>
                {viceStatus(party)} O convidado aceita ou recusa na tela dele e segue no partido dele. Um novo convite
                ocupa o lugar do anterior.
              </FieldDescription>
              {invitedNickname !== null && (
                <Button
                  variant="outline"
                  size="sm"
                  className="justify-self-start"
                  disabled={withdrawVice.isPending}
                  onClick={() => withdrawVice.mutate()}
                >
                  Retirar convite
                </Button>
              )}
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
              <AlertDescription>
                Chapa, filiados, contribuições e promessa são públicos desde o primeiro dia.
              </AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <DisabledHint reason={blockedReason}>
            <Button
              disabled={!candidate || setTicket.isPending}
              onClick={() => setTicket.mutate({ candidate }, { onSuccess: () => onOpenChange(false) })}
            >
              Inscrever a chapa
            </Button>
          </DisabledHint>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/** A linha de estado do convite de vice da chapa. */
function viceStatus(party: ElectionParty) {
  const nickname = party.vice?.nickname;
  if (!nickname || party.vice_phase === "NONE") return "Sem vice, a chapa concorre só com o candidato.";
  if (party.vice_phase === "ACCEPTED") return `${nickname} aceitou ser vice.`;
  if (party.vice_phase === "DECLINED") return `${nickname} recusou o convite.`;
  return `Aguardando a resposta de ${nickname}; até lá a chapa concorre sem vice.`;
}
