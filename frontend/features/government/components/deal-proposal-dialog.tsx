import { useState } from "react";
import { CircleCheck, Landmark, ShieldAlert, TrendingUp, Undo2 } from "lucide-react";
import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
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
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { useAnswerDeal } from "../hooks/mutations/useAnswerDeal";
import { useBase } from "../hooks/queries/useBase";
import { baseOutlook, groupsLabel, monthlyLabel, yearShare } from "../lib/base";
import { SECTOR_BOOST } from "../lib/government-metrics";
import { addressOf, amendmentSentence, NO_SECTOR, WHOLE_SECTOR } from "../lib/sector-address";
import { SectorSegmentSelect } from "./sector-segment-select";

type DealProposalDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

/** A proposta do governo ao partido de quem vê: o que ele recebe, o que perde e o prazo para responder. */
export function DealProposalDialog({ open, onOpenChange }: DealProposalDialogProps) {
  const { data: base } = useBase({ enabled: open });
  const { data: panel } = useGovernment({ enabled: open });
  const answer = useAnswerDeal();
  const [sector, setSector] = useState(NO_SECTOR);
  const [segment, setSegment] = useState(WHOLE_SECTOR);
  const proposal = base?.my_proposal;
  if (!base || !proposal || proposal.answer_by === null) return null;

  // Só aceitar leva o endereço da emenda; a recusa vai sem setor
  const respond = (accept: boolean) =>
    answer.mutate(accept ? { accept, ...addressOf(sector, segment) } : { accept }, {
      onSuccess: () => onOpenChange(false),
    });
  const until = displayDayMonth(proposal.answer_by);
  const governing = base.governing_abbr ?? "governo";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-125">
        <DialogHeader variant="divided">
          <DialogTitle>
            O governo {base.president} propõe que o {proposal.abbr} entre na base
          </DialogTitle>
          <DialogDescription>Acordo de apoio por emenda · responda até {until}.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-3.5">
            <div className="grid gap-2.5 sm:grid-cols-3">
              <Kpi
                label="Emenda"
                value={
                  <span className="text-lg">
                    {monthlyLabel(proposal.monthly)}{" "}
                    <span className="text-xs font-normal text-muted-foreground">/mês</span>
                  </span>
                }
                note={`${yearShare(proposal.ratio)} do PIB por ano`}
              />
              <Kpi
                label="Prazo"
                value={<span className="text-lg">até o fim do mandato</span>}
                note="a partir da sua resposta"
              />
              <Kpi
                label="Base do governo"
                value={
                  <span className="text-lg">
                    {base.seats} → <span className="text-success">{proposal.base_after}</span>
                  </span>
                }
                note={baseOutlook(proposal.base_after, base.majority, base.impeachment_votes)}
              />
            </div>

            {/* Endereço da emenda */}
            <SectorSegmentSelect
              sectors={panel?.sectors ?? []}
              sector={sector}
              segment={segment}
              onChange={(nextSector, nextSegment) => {
                setSector(nextSector);
                setSegment(nextSegment);
              }}
              label="Setor da emenda"
              noneLabel="Sem endereço"
              segmentScope="recebem a emenda"
            />

            <ul className="grid rounded-lg border px-3 py-1 text-[13px]">
              <Line icon={CircleCheck}>
                Você, como líder, orienta <b>Sim</b> em tudo o que o governo propuser. Até um terço da bancada ainda
                pode desobedecer, como em qualquer votação.
              </Line>
              <Line icon={TrendingUp}>
                A emenda chega às suas bases: {groupsLabel(proposal.ally_groups).toLowerCase()} sobem o apoio ao{" "}
                {proposal.abbr}, cerca de +1 por mês.
              </Line>
              {sector !== NO_SECTOR && (
                <Line icon={Landmark}>
                  <span className="inline-flex flex-wrap items-center gap-1">
                    Com o endereço, {amendmentSentence(proposal.sector_boost)}.
                    <MetricHint metric={SECTOR_BOOST} />
                  </span>
                </Line>
              )}
              <Line icon={ShieldAlert}>
                Orientar Não ou sair antes do prazo rompe o acordo:{" "}
                {groupsLabel(proposal.government_groups).toLowerCase()} somam +8 de rejeição ao {proposal.abbr}. Se o{" "}
                {governing} cortar a emenda, o peso cai nele.
              </Line>
              <Line icon={Undo2}>Sem resposta até {until}, conta como recusa. Recusar não custa nada.</Line>
            </ul>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" disabled={answer.isPending} onClick={() => respond(false)}>
            Recusar
          </Button>
          <Button disabled={answer.isPending} onClick={() => respond(true)}>
            Aceitar e entrar na base
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Line({ icon: Icon, children }: { icon: typeof Undo2; children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2.5 py-2">
      <Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <span>{children}</span>
    </li>
  );
}
