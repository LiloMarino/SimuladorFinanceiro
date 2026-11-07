import { useState } from "react";
import { Ban, CircleCheck, Coins, Flag, Mic, ShieldAlert, Users } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { PartyMarkPair } from "@/shared/components/party-mark-pair";
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
import { Input } from "@/shared/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { defaultFederationName } from "@/shared/lib/federation-name";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMoneyWhole, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { useProposeFederation } from "../hooks/mutations/useProposeFederation";
import { useFederationPreview } from "../hooks/queries/useFederationPreview";
import { federationCandidates, rejectionDelta } from "../lib/federation";
import { GROUP_INFO } from "../lib/voters";

type FederationProposeDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: ElectionPanel;
  party: ElectionParty;
};

/** O fundador escolhe o partido, o candidato e o nome da federação e vê o que ela muda antes de enviar. */
export function FederationProposeDialog({ open, onOpenChange, panel, party }: FederationProposeDialogProps) {
  const [partnerChoice, setPartnerChoice] = useState<number | null>(null);
  const [candidateChoice, setCandidateChoice] = useState<string | null>(null);
  const [nameChoice, setNameChoice] = useState<string | null>(null);
  const propose = useProposeFederation();

  const options = panel.federation_options
    .map((option) => ({ option, other: panel.parties.find((candidate) => candidate.id === option.party_id) }))
    .filter((entry): entry is { option: typeof entry.option; other: ElectionParty } => entry.other !== undefined);

  const partnerId = partnerChoice ?? options.find((entry) => entry.option.blocked === null)?.other.id ?? null;
  const partner = options.find((entry) => entry.other.id === partnerId)?.other;

  const candidates = partner ? federationCandidates(party, partner) : [];
  const candidate = candidates.find((entry) => entry.key === candidateChoice) ?? candidates[0];
  const name = nameChoice ?? (partner ? defaultFederationName(party.abbr, partner.abbr) : "");

  const { data: preview } = useFederationPreview(
    partner && candidate ? { partner_id: partner.id, candidate_party_id: candidate.partyId } : null,
  );

  const send = () => {
    if (!partner || !candidate) return;
    propose.mutate(
      {
        partner_id: partner.id,
        name: name.trim(),
        candidate_party_id: candidate.partyId,
        candidate: candidate.nickname,
      },
      { onSuccess: () => onOpenChange(false) },
    );
  };

  const electionYear = preview?.election_year;
  const sum = preview ? Number(preview.own_share) + Number(preview.partner_share) : 0;
  const orienting = preview && preview.orienting_party_id === party.id ? party : partner;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-150">
        <DialogHeader variant="divided">
          <DialogTitle>Propor federação</DialogTitle>
          <DialogDescription>
            O {party.abbr} e o parceiro viram um partido só na eleição de {electionYear ?? "…"} e no mandato seguinte.
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-4">
            {/* Parceiro */}
            <div className="grid gap-2">
              <span className="text-sm font-medium">Com qual partido</span>
              <div role="radiogroup" aria-label="Parceiro" className="grid gap-2">
                {options.map(({ option, other }) => {
                  const selected = other.id === partnerId;
                  return (
                    <button
                      key={other.id}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      disabled={option.blocked !== null}
                      onClick={() => {
                        setPartnerChoice(other.id);
                        setCandidateChoice(null);
                        setNameChoice(null);
                      }}
                      className={cn(
                        "grid grid-cols-[auto_1fr] items-center gap-x-2.5 gap-y-0.5 rounded-[10px] border px-3 py-2 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-60",
                        selected && "border-2 border-primary",
                      )}
                    >
                      <PartyMark abbr={other.abbr} color={other.color} size="md" />
                      <b className="text-[13px]">{other.name}</b>
                      <span />
                      <span className="text-xs text-muted-foreground">
                        {option.blocked ??
                          `${other.is_computer ? "Computador" : "Jogadores"} · ${displayPercent(Number(other.intention_points) / 100, 1)} na pesquisa${option.below_barrier ? " · abaixo da barreira" : ""}`}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {partner && candidate && (
              <>
                <div className="grid gap-3 sm:grid-cols-2">
                  {/* Candidato da chapa */}
                  <Field>
                    <FieldLabel>Candidato da chapa</FieldLabel>
                    <Select
                      value={candidate.key}
                      items={Object.fromEntries(candidates.map((entry) => [entry.key, entry.label]))}
                      onValueChange={(value) => value && setCandidateChoice(value)}
                    >
                      <SelectTrigger className="w-full" aria-label="Candidato da chapa">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {candidates.map((entry) => (
                          <SelectItem key={entry.key} value={entry.key}>
                            <span>{entry.label}</span>
                            <span className="text-xs text-muted-foreground">{entry.abbr}</span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FieldDescription>O vice sai de qualquer partido da federação, depois.</FieldDescription>
                  </Field>

                  {/* Nome */}
                  <Field>
                    <FieldLabel>Nome</FieldLabel>
                    <Input
                      value={name}
                      maxLength={60}
                      aria-label="Nome da federação"
                      onChange={(event) => setNameChoice(event.target.value)}
                    />
                    <FieldDescription>Aparece na urna, no Congresso e no jornal.</FieldDescription>
                  </Field>
                </div>

                {/* O que muda */}
                {preview && (
                  <div className="grid gap-2.5 rounded-lg border px-3.5 py-3 text-[13px]">
                    <span className="font-semibold">O que muda para o {party.abbr}</span>
                    <Line icon={CircleCheck} tone="success">
                      {displayPercent(preview.own_share, 1)} + {displayPercent(preview.partner_share, 1)} ={" "}
                      <b>{displayPercent(sum, 1)}</b> somados na barreira de {displayPercent(preview.barrier, 0)} e na
                      divisão das cadeiras. <b>Uma lista no Congresso:</b> os dois partidos elegem juntos e as cadeiras
                      se repartem entre eles depois.
                    </Line>
                    <Line icon={Users}>
                      {candidate.label} concorre pelos dois;{" "}
                      {candidate.partyId === party.id ? partner.abbr : party.abbr} deixa de ter candidato. O fundador do{" "}
                      {candidate.abbr} escolhe o vice e as promessas.
                    </Line>
                    <Line icon={Mic}>
                      A orientação da bancada é a do {orienting?.abbr}, o partido com mais cadeiras; o parceiro não
                      orienta, e os deputados dele desobedecem pelo sorteio.
                    </Line>
                    <Line icon={Flag}>
                      A chapa leva as promessas de {candidate.abbr}
                      {preview.leaving_promises > 0
                        ? `; as ${preview.leaving_promises} de ${candidate.partyId === party.id ? partner.abbr : party.abbr} saem sem custo`
                        : ""}
                      .
                    </Line>
                    <Line icon={Coins}>
                      Verba: cada partido continua com a sua ({party.abbr} {displayMoneyWhole(preview.own_budget)} ·{" "}
                      {partner.abbr} {displayMoneyWhole(preview.partner_budget)}) e faz as próprias ações de campanha.
                    </Line>
                    <Line icon={ShieldAlert} tone="warning">
                      Vale de {displayDayMonth(preview.in_force_from)} até {displayShortDate(preview.ends_on)}. Quem
                      sair antes desfaz a federação para os dois e fica impedido de se federar na eleição seguinte.
                    </Line>
                    <Line icon={Ban}>
                      Os dois herdam metade da rejeição um do outro, por grupo, como mostra a tabela.
                    </Line>

                    <div className="overflow-hidden rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Rejeição por grupo</TableHead>
                            <TableHead className="text-right">{party.abbr} hoje</TableHead>
                            <TableHead className="text-right">{partner.abbr}</TableHead>
                            <TableHead className="text-right">{party.abbr} federado</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {preview.rejection.map((row) => {
                            const delta = rejectionDelta(row);
                            return (
                              <TableRow key={row.group}>
                                <TableCell>{GROUP_INFO[row.group].label}</TableCell>
                                <TableCell numeric>{Math.round(Number(row.own))}%</TableCell>
                                <TableCell numeric>{Math.round(Number(row.partner))}%</TableCell>
                                <TableCell numeric>
                                  <b>{Math.round(Number(row.federated))}%</b>{" "}
                                  <span className="text-xs text-destructive">{delta}</span>
                                </TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-between">
          <span className="flex items-center gap-2 text-xs text-muted-foreground">
            {partner && preview && (
              <>
                <PartyMarkPair parties={[party, partner]} size="sm" />O {partner.abbr} responde até{" "}
                {displayDayMonth(preview.answer_until)}
              </>
            )}
          </span>
          <span className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button disabled={!partner || !candidate || name.trim() === "" || propose.isPending} onClick={send}>
              Enviar proposta
            </Button>
          </span>
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
        className={cn(
          "mt-0.5 size-4 shrink-0",
          tone === "success" ? "text-success" : tone === "warning" ? "text-warning" : "text-muted-foreground",
        )}
      />
      <span>{children}</span>
    </div>
  );
}
