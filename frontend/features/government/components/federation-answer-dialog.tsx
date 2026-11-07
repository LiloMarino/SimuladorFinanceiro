import { CircleCheck, Flag, Lock, Mic, Users } from "lucide-react";
import { PartyMarkPair } from "@/shared/components/party-mark-pair";
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
import { displayDayMonth, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, FederationProposal } from "@/types";
import { useAnswerFederation } from "../hooks/mutations/useAnswerFederation";

type FederationAnswerDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  /** O partido de quem vê, o convidado */
  party: ElectionParty;
  proposal: FederationProposal;
};

/** A proposta de federação ao partido de quem vê: o que a lista muda, até quando prende e o prazo para responder. */
export function FederationAnswerDialog({ open, onOpenChange, panel, party, proposal }: FederationAnswerDialogProps) {
  const answer = useAnswerFederation();
  const sender = panel.parties.find((candidate) => candidate.id === proposal.from_party_id);
  const orienting = panel.parties.find((candidate) => candidate.id === proposal.orienting_party_id);
  const candidateParty = panel.parties.find((candidate) => candidate.id === proposal.candidate_party_id);
  if (!sender) return null;

  const respond = (accept: boolean) => answer.mutate({ accept }, { onSuccess: () => onOpenChange(false) });
  const ownShare = Number(party.intention_points) / 100;
  const senderShare = Number(sender.intention_points) / 100;
  const until = displayShortDate(proposal.ends_on);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>
            <span className="flex items-center gap-2.5">
              <PartyMarkPair parties={[sender, party]} size="md" />O {sender.abbr} propõe federação ao {party.abbr}
            </span>
          </DialogTitle>
          <DialogDescription>
            Proposta de {displayDayMonth(proposal.sent_on)} · responda até {displayDayMonth(proposal.expires_on)}; sem
            resposta, ela expira.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 rounded-lg border px-3.5 py-3 text-[13px]">
              <dt className="text-muted-foreground">Nome</dt>
              <dd className="font-medium">{proposal.name}</dd>
              <dt className="text-muted-foreground">Candidato</dt>
              <dd className="font-medium">
                {proposal.candidate} ({candidateParty?.abbr})
              </dd>
              <dt className="text-muted-foreground">Na pesquisa</dt>
              <dd className="font-medium">
                {party.abbr} {displayPercent(ownShare, 1)} + {sender.abbr} {displayPercent(senderShare, 1)} ={" "}
                {displayPercent(ownShare + senderShare, 1)}
              </dd>
              <dt className="text-muted-foreground">Orientação</dt>
              <dd className="font-medium">do {orienting?.abbr}, pela regra de mais cadeiras</dd>
            </dl>

            <div className="grid gap-2.5 rounded-lg border px-3.5 py-3 text-[13px]">
              <span className="font-semibold">Se você aceitar</span>
              <Line icon={CircleCheck} tone="success">
                Os dois partidos entram numa lista só: a barreira e a divisão das cadeiras usam a soma, e as cadeiras se
                repartem entre eles depois.
              </Line>
              <Line icon={Flag}>
                A chapa leva as promessas de {candidateParty?.abbr}
                {candidateParty?.id === party.id
                  ? "; as do " + sender.abbr + " saem sem custo."
                  : "; as suas saem sem custo e você não define promessas enquanto a federação disputa."}
              </Line>
              <Line icon={Lock} tone="warning">
                Presos até {until}. Quem sair antes desfaz a federação para os dois e fica impedido de se federar na
                eleição seguinte.
              </Line>
              <Line icon={Users}>
                Cada partido herda metade da rejeição do outro, por grupo, e continua com a própria verba e as próprias
                ações de campanha.
              </Line>
              <Line icon={Mic}>
                O {orienting?.abbr} orienta a bancada; o parceiro não orienta, e os deputados dele desobedecem pelo
                sorteio.
              </Line>
            </div>

            {!panel.can_federate && (
              <Alert variant="info">
                <AlertDescription>
                  Os filiados do {party.abbr} veem o aviso; quem responde é o fundador, {party.founder}.
                </AlertDescription>
              </Alert>
            )}
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" disabled={!panel.can_federate || answer.isPending} onClick={() => respond(false)}>
            Recusar
          </Button>
          <Button disabled={!panel.can_federate || answer.isPending} onClick={() => respond(true)}>
            Aceitar a federação
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Line({
  icon: Icon,
  tone,
  children,
}: {
  icon: typeof Users;
  tone?: "success" | "warning";
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-2.5 leading-normal">
      <Icon
        className={
          tone === "success"
            ? "mt-0.5 size-4 shrink-0 text-success"
            : tone === "warning"
              ? "mt-0.5 size-4 shrink-0 text-warning"
              : "mt-0.5 size-4 shrink-0 text-muted-foreground"
        }
      />
      <span>{children}</span>
    </div>
  );
}
