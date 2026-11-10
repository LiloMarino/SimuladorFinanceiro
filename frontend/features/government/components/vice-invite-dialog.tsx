import { CircleCheck, Handshake, TriangleAlert, Undo2, Users } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
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
import type { ElectionPanel, ElectionParty } from "@/types";
import { useAnswerVice } from "../hooks/mutations/useAnswerVice";
import { PartyMark } from "@/shared/components/party-mark";
import { ValueChips } from "@/shared/components/value-chip";

type ViceInviteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
};

/** Os convites de vice de quem vê, lado a lado: o jogador compara as chapas e aceita uma só. */
export function ViceInviteDialog({ open, onOpenChange, panel }: ViceInviteDialogProps) {
  const answer = useAnswerVice();
  const invites = panel.my_vices
    .filter((vice) => vice.phase === "PENDING")
    .map((vice) => panel.parties.find((candidateParty) => candidateParty.id === vice.party_id))
    .filter((party): party is ElectionParty => party !== undefined);
  if (invites.length === 0) return null;

  // A pesquisa só existe depois da primeira atualização semanal: antes, todos os partidos têm 0 ponto
  const pollPublished = panel.parties.some((candidateParty) => Number(candidateParty.intention_points) > 0);

  const homeParty = panel.parties.find((candidateParty) => candidateParty.id === panel.my_party?.party_id);
  const staysIn = homeParty ? `Você continua no ${homeParty.abbr}.` : "Você continua sem partido.";
  const respond = (party: ElectionParty, accept: boolean) =>
    answer.mutate(
      { party_id: party.id, accept },
      { onSuccess: () => (accept || invites.length === 1) && onOpenChange(false) },
    );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>
            {invites.length === 1 ? "Convite para vice" : `${invites.length} convites para vice`}
          </DialogTitle>
          <DialogDescription>
            Eleição de {displayMonthShort(panel.dates.first_round)} {panel.election_year} · responda até{" "}
            {displayDayMonth(panel.dates.ticket_deadline)}; sem resposta, a chapa concorre sem vice.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            {invites.length > 1 && (
              <Alert variant="warning">
                <TriangleAlert />
                <AlertDescription>
                  Aceitar um convite recusa os outros, e as outras chapas são avisadas.
                </AlertDescription>
              </Alert>
            )}

            {invites.map((party) => {
              const founder = party.founder ?? party.name;
              const candidate = party.candidate?.name ?? founder;
              const lines = [
                { icon: Users, text: `Se o ${party.abbr} vencer, ${candidate} é o eleito e você é o vice.` },
                { icon: Handshake, text: staysIn },
                { icon: CircleCheck, text: `${founder} convidou você; a chapa concorre sem vice até a sua resposta.` },
                {
                  icon: Undo2,
                  text: `Recusar não muda nada para você: a vaga volta para ${founder} indicar outro jogador.`,
                },
              ];
              return (
                <section key={party.id} className="grid gap-3 rounded-[10px] border p-3">
                  <div className="flex items-center gap-3">
                    <PartyMark abbr={party.abbr} color={party.color} size="lg" />
                    <span className="grid flex-1 gap-0.5">
                      <b>{party.name}</b>
                      <span className="text-xs text-muted-foreground">
                        Candidato: {candidate} ·{" "}
                        {pollPublished &&
                          `${Number(party.intention_points).toLocaleString("pt-BR", { maximumFractionDigits: 0 })}% na pesquisa · `}
                        verba de {displayMoney(party.budget)}/mês
                      </span>
                    </span>
                  </div>

                  <div className="grid gap-1.5">
                    <span className="text-sm font-medium">Bandeiras do partido</span>
                    <ValueChips values={party.flags} />
                  </div>

                  <ul className="grid rounded-lg border px-3 py-1">
                    {lines.map((line) => (
                      <li key={line.text} className="flex items-start gap-2.5 py-2 text-[13px]">
                        <line.icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                        {line.text}
                      </li>
                    ))}
                  </ul>

                  <div className="flex justify-end gap-2">
                    <Button variant="outline" disabled={answer.isPending} onClick={() => respond(party, false)}>
                      Recusar
                    </Button>
                    <Button disabled={answer.isPending} onClick={() => respond(party, true)}>
                      Aceitar e entrar na chapa
                    </Button>
                  </div>
                </section>
              );
            })}
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
