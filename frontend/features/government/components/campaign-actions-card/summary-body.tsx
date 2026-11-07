import { Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { CampaignActionKind, CampaignPanel, CampaignTarget, VoterGroup } from "@/types";
import {
  ACTION_INFO,
  bandEffect,
  bandOf,
  freshGroup,
  groupWord,
  nthOf,
  monthLabel,
  nextMonthLabel,
  ratePercent,
  repairUsed,
  signed,
} from "../../lib/campaign";
import { BandsTable } from "../campaign-dice";
import { SummaryRow } from "./summary-row";

type SummaryBodyProps = {
  campaign: CampaignPanel;
  kind: CampaignActionKind;
  group: VoterGroup;
  target: CampaignTarget;
  rival: string | undefined;
};

/** A tabela de faixas do resumo e as linhas de média, reparo e valor no dia da eleição. */
export function SummaryBody({ campaign, kind, group, target, rival }: SummaryBodyProps) {
  const normal = target.bands.find((band) => band.band === "NORMAL");
  const disaster = bandOf(target.bands, 1);
  const average = Number(target.average);
  const atVote = Math.round(Number(campaign.share_at_vote) * 100);
  const repeat = target.uses_this_month > 0;
  const full = kind === "EVENT" && Number(target.repair_left) === 0;
  // O grupo ainda sem uso onde a mesma ação renderia 100%
  const fresh = freshGroup(campaign.actions.find((candidate) => candidate.action === kind)?.targets ?? []);

  const subject =
    kind === "TV"
      ? "apoio em cada grupo"
      : kind === "ATTACK"
        ? `apoio do ${rival ?? "rival"} entre ${groupWord(group)}`
        : `apoio entre ${groupWord(group)}`;

  return (
    <>
      {repeat && (
        <Alert variant="warning">
          <Info />
          <AlertTitle>
            Rende {ratePercent(target.rate)}: é {nthOf(kind, target.uses_this_month + 1)}{" "}
            {kind === "TV" ? "TV" : ACTION_INFO[kind].noun.toLowerCase()}
            {kind === "TV" ? "" : ` com ${groupWord(group)}`} em {monthLabel(campaign.today)}
          </AlertTitle>
          <AlertDescription>
            {[...repeatNote(kind, target, fresh), `Em ${nextMonthLabel(campaign.today)} volta a 100%.`].join(" ")}
          </AlertDescription>
        </Alert>
      )}
      {full && (
        <Alert variant="warning">
          <Info />
          <AlertTitle>Rejeição já reparada no limite</AlertTitle>
          <AlertDescription>
            O {campaign.party_abbr} reparou {repairUsed(target)} de {target.repair_limit} neste grupo na campanha: o
            evento só soma apoio.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-1.5">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-xs font-medium text-muted-foreground">O dado decide quanto rende</span>
          <span className="text-right text-xs text-faint-foreground">
            {kind === "RALLY" && "extremos dobrados · "}
            {subject}
          </span>
        </div>
        <BandsTable bands={target.bands} />
      </div>

      <div className="grid gap-1 text-[12.5px]">
        <SummaryRow label="Em média" tone="up">
          {kind === "TV"
            ? `${signed(average, 1)} em cada grupo`
            : kind === "ATTACK"
              ? `${signed(average, 1)} do ${rival ?? "rival"}`
              : `${signed(average, 1)} de apoio`}
        </SummaryRow>
        {kind === "EVENT" && normal && (
          <SummaryRow label="Rejeição reparada (fora o desastre)">
            {signed(normal.rejection)} · {repairUsed(target)} de {target.repair_limit} usados
          </SummaryRow>
        )}
        {kind === "RALLY" && disaster && (
          <SummaryRow label="Chance de tombo grande" tone="down">
            {displayPercent(disaster.chance, 2, { trim: true })} · {bandEffect(disaster)}
          </SummaryRow>
        )}
        {kind === "ATTACK" && disaster && (
          <>
            <SummaryRow label="Sai pela culatra" tone="down">
              {displayPercent(disaster.chance, 2, { trim: true })} · {signed(disaster.rejection)} de rejeição a você
            </SummaryRow>
            <SummaryRow label="Todo ataque é público">sim</SummaryRow>
          </>
        )}
        <SummaryRow label={`No 1º turno, em ${displayDayMonth(campaign.first_round)}, vale`}>~{atVote}%</SummaryRow>
      </div>
    </>
  );
}

/** "Duda fez o 1º em 3 ago." e "Num grupo novo rende 100%: com servidores, +6."; a TV não tem grupo novo. */
function repeatNote(kind: CampaignActionKind, target: CampaignTarget, fresh: ReturnType<typeof freshGroup>) {
  if (kind === "TV" || !target.first_day) return [];
  const notes = [`${target.first_by ?? "O partido"} fez ${nthOf(kind, 1)} em ${displayDayMonth(target.first_day)}.`];
  if (fresh) notes.push(`Num grupo novo rende 100%: com ${groupWord(fresh.group)}, ${fresh.effect}.`);
  return notes;
}
