import { CircleCheck, Handshake, Undo2, Users } from "lucide-react";
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
import { displayDayMonth, displayMoney, displayMonthShort } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { useAnswerVice } from "../hooks/mutations/useAnswerVice";
import { PartyMark, PersonMark } from "./party-mark";
import { PromiseRuler } from "./promise-ruler";

type ViceInviteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
};

/** O convite de vice: o que o jogador indicado, de qualquer partido, vê antes de aceitar ou recusar. */
export function ViceInviteDialog({ open, onOpenChange, panel }: ViceInviteDialogProps) {
  const answer = useAnswerVice();
  const party = panel.parties.find((candidateParty) => candidateParty.id === panel.my_vice?.party_id);
  if (!party) return null;

  const founder = party.founder ?? party.name;
  const candidate = party.candidate?.name ?? founder;
  const respond = (accept: boolean) => answer.mutate({ accept }, { onSuccess: () => onOpenChange(false) });

  const homeParty = panel.parties.find((candidateParty) => candidateParty.id === panel.my_party?.party_id);
  const staysIn =
    homeParty && homeParty.id !== party.id
      ? `Você continua no ${homeParty.abbr} e soma para ele no ranking.`
      : homeParty
        ? `Você continua no ${homeParty.abbr}.`
        : "Você continua sem partido.";

  const lines = [
    { icon: Users, text: `Se o ${party.abbr} vencer, ${candidate} é o eleito e você é o vice.` },
    { icon: Handshake, text: staysIn },
    {
      icon: CircleCheck,
      text: `Sem resposta até ${displayDayMonth(panel.dates.ticket_deadline)}, a chapa concorre sem vice.`,
    },
    {
      icon: Undo2,
      text: `Recusar não muda nada para você: a vaga volta para ${founder} indicar outro jogador.`,
    },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>{founder} indicou você para vice</DialogTitle>
          <DialogDescription>
            Chapa do {party.abbr} para a eleição de {displayMonthShort(panel.dates.first_round)} {panel.election_year} ·
            responda até {displayDayMonth(panel.dates.ticket_deadline)}.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <div className="flex items-center gap-3 rounded-[10px] border p-3">
              <PartyMark abbr={party.abbr} color={party.color} size="lg" />
              <span className="grid flex-1 gap-0.5">
                <b>{party.name}</b>
                <span className="text-xs text-muted-foreground">
                  Candidato: {candidate} ·{" "}
                  {Number(party.intention_points).toLocaleString("pt-BR", { maximumFractionDigits: 0 })}% na pesquisa ·
                  verba de {displayMoney(party.budget)}/mês
                </span>
              </span>
            </div>

            <div className="grid gap-1.5">
              <span className="text-sm font-medium">Promessa do partido</span>
              <PromiseRuler
                showEnds
                markers={[
                  {
                    key: party.id,
                    promise: party.promise,
                    node: party.candidate ? (
                      <PersonMark person={party.candidate} />
                    ) : (
                      <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                    ),
                  },
                ]}
              />
            </div>

            <ul className="grid rounded-lg border px-3 py-1">
              {lines.map((line) => (
                <li key={line.text} className="flex items-start gap-2.5 py-2 text-[13px]">
                  <line.icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                  {line.text}
                </li>
              ))}
            </ul>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" disabled={answer.isPending} onClick={() => respond(false)}>
            Recusar
          </Button>
          <Button disabled={answer.isPending} onClick={() => respond(true)}>
            Aceitar e entrar na chapa
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
