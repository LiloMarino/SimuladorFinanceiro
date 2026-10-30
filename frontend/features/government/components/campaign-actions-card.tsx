import { useRef, useState } from "react";
import { Lock, Dices, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type {
  CampaignAction,
  CampaignActionKind,
  CampaignPanel,
  CampaignTarget,
  VoterGroup,
  VoterGroupInfo,
} from "@/types";
import {
  ACTION_INFO,
  bandEffect,
  bandOf,
  chancePercent,
  freshGroup,
  groupWord,
  nthOf,
  monthLabel,
  nextMonthLabel,
  ratePercent,
  repairUsed,
  signed,
  targetOf,
} from "../lib/campaign";
import { dayAfter } from "../lib/runoff";
import { GROUP_INFO } from "../lib/voters";
import { ActionIcon } from "./campaign-action-icon";
import { BandsTable } from "./campaign-dice";
import { CampaignRollDialog } from "./campaign-roll-dialog";
import { PartyMark } from "./party-mark";
import { GroupIcon } from "./value-chip";

type CampaignActionsCardProps = {
  campaign: CampaignPanel;
  /** Os grupos de eleitores, para o peso de cada um */
  groups: VoterGroupInfo[];
  /** O caixa de quem vê, de onde a ação é paga na hora */
  cash: string | undefined;
};

/** As quatro ações avulsas de campanha em passos (ação, grupo, rival), com o resumo do dado sempre à vista. */
export function CampaignActionsCard({ campaign, groups, cash }: CampaignActionsCardProps) {
  const [kind, setKind] = useState<CampaignActionKind>("EVENT");
  const [group, setGroup] = useState<VoterGroup>("RETIREES");
  const [chosenRival, setChosenRival] = useState<number | null>(null);
  const [rolling, setRolling] = useState(false);
  const top = useRef<HTMLDivElement>(null);

  const weights = new Map(groups.map((info) => [info.group, info.weight]));
  // No 2º turno cada grupo mostra os indecisos que as ações disputam
  const undecided = campaign.groups.some((item) => item.undecided !== null)
    ? new Map(campaign.groups.map((item) => [item.group, item.undecided]))
    : null;
  const action = campaign.actions.find((candidate) => candidate.action === kind);
  const rivalId = chosenRival ?? (campaign.rivals.length === 1 ? (campaign.rivals[0]?.party_id ?? null) : null);
  const rival = campaign.rivals.find((candidate) => candidate.party_id === rivalId);
  const cashNumber = cash === undefined ? null : Number(cash);

  /** O que falta no caixa para pagar a ação; o servidor calculou ao montar o cartão, e o caixa vivo corrige */
  const missing = (candidate: CampaignAction) =>
    cashNumber === null ? Number(candidate.missing) : Math.max(0, Number(candidate.price) - cashNumber);

  return (
    <Card>
      <CardContent>
        <div ref={top} className="grid scroll-mt-4 gap-4">
          {/* Cabeçalho */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Ações de campanha</h2>
              <span className="text-[13px] text-muted-foreground">
                Qualquer filiado faz e paga na hora, da própria carteira. O resultado sai de um dado e só o{" "}
                {campaign.party_abbr} vê.
              </span>
            </div>
            <Badge variant="secondary">
              <Lock />
              Só o {campaign.party_abbr} vê
            </Badge>
          </div>

          {!campaign.open || !action ? (
            <Alert variant="muted">
              <Info />
              <AlertTitle>As ações fecharam</AlertTitle>
              <AlertDescription>{campaign.closed_reason}</AlertDescription>
            </Alert>
          ) : (
            <ActionBody
              campaign={campaign}
              action={action}
              kind={kind}
              onKind={setKind}
              group={group}
              onGroup={setGroup}
              rivalId={rivalId}
              onRival={setChosenRival}
              weights={weights}
              undecided={undecided}
              cash={cashNumber}
              missing={missing}
              onRoll={() => setRolling(true)}
            />
          )}
        </div>
      </CardContent>

      {rolling && action && (
        <CampaignRollDialog
          action={action}
          target={targetOf(action.targets, kind === "TV" ? null : group) ?? action.targets[0]!}
          request={{ action: kind, group: kind === "TV" ? null : group, rival_id: kind === "ATTACK" ? rivalId : null }}
          title={summaryTitle(kind, group, rival?.abbr ?? null)}
          subtitle={rollSubtitle(campaign, action, targetOf(action.targets, kind === "TV" ? null : group))}
          partyAbbr={campaign.party_abbr}
          rivalAbbr={rival?.abbr ?? null}
          onClose={() => setRolling(false)}
          onAnother={() => {
            setRolling(false);
            top.current?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
        />
      )}
    </Card>
  );
}

function summaryTitle(kind: CampaignActionKind, group: VoterGroup, rival: string | null) {
  switch (kind) {
    case "TV":
      return "TV";
    case "EVENT":
      return `Evento com ${groupWord(group)}`;
    case "RALLY":
      return `Comício com ${groupWord(group)}`;
    case "ATTACK":
      return `Ataque ao ${rival ?? "rival"} entre ${groupWord(group)}`;
  }
}

/** "2ª vez em ago · rende 50% · ganho normal +3": o que a pessoa lê antes de pagar o dado. */
function rollSubtitle(campaign: CampaignPanel, action: CampaignAction, target: CampaignTarget | undefined) {
  if (!target) return "";
  const normal = target.bands.find((band) => band.band === "NORMAL");
  const parts = [
    `${target.uses_this_month + 1}ª vez em ${monthLabel(campaign.today)}`,
    `rende ${ratePercent(target.rate)}`,
  ];
  if (normal) parts.push(`ganho normal ${bandEffect(normal)}`);
  return parts.join(" · ") + (action.advantage ? " · dois dados" : "");
}

type ActionBodyProps = {
  campaign: CampaignPanel;
  action: CampaignAction;
  kind: CampaignActionKind;
  onKind: (kind: CampaignActionKind) => void;
  group: VoterGroup;
  onGroup: (group: VoterGroup) => void;
  rivalId: number | null;
  onRival: (id: number) => void;
  weights: Map<VoterGroup, string>;
  undecided: Map<VoterGroup, string | null> | null;
  cash: number | null;
  missing: (action: CampaignAction) => number;
  onRoll: () => void;
};

function ActionBody({
  campaign,
  action,
  kind,
  onKind,
  group,
  onGroup,
  rivalId,
  onRival,
  weights,
  undecided,
  cash,
  missing,
  onRoll,
}: ActionBodyProps) {
  const isTv = kind === "TV";
  const isAttack = kind === "ATTACK";
  const target = targetOf(action.targets, isTv ? null : group);
  const rival = campaign.rivals.find((candidate) => candidate.party_id === rivalId);
  const price = Number(action.price);
  const short = missing(action);

  const ready = !!target && short === 0 && (!isAttack || rivalId !== null);

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="grid min-w-0 content-start gap-4.5">
        {/* Passo 1: a ação */}
        <div className="grid gap-2">
          <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">1 · Ação</span>
          <div role="radiogroup" aria-label="Ação" className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-4">
            {campaign.actions.map((candidate) => (
              <ActionChoice
                key={candidate.action}
                action={candidate}
                selected={candidate.action === kind}
                short={missing(candidate)}
                cash={cash}
                noRival={candidate.action === "ATTACK" && campaign.rivals.length === 0}
                partyAbbr={campaign.party_abbr}
                onSelect={() => onKind(candidate.action)}
              />
            ))}
          </div>
        </div>

        {/* TV: atinge todos os grupos */}
        {isTv && <TvReach weights={weights} />}

        {/* Passo 2: o grupo */}
        {!isTv && (
          <div className="grid gap-2">
            <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
              <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                2 · Grupo
              </span>
              <span className="text-xs text-faint-foreground">
                {undecided
                  ? `Repetir a ação no mesmo grupo rende 100%, 50%, 25%, contando desde ${displayDayMonth(dayAfter(campaign.first_round))}; o ganho sai primeiro dos indecisos do grupo`
                  : `Repetir a ação no mesmo grupo no mês rende 100%, 50%, 25%; em ${nextMonthLabel(campaign.today)} volta a 100%`}
              </span>
            </div>
            <GroupChoices
              action={action}
              kind={kind}
              group={group}
              onGroup={onGroup}
              weights={weights}
              undecided={undecided}
              today={campaign.today}
            />
          </div>
        )}

        {/* Passo 3: o rival, só no ataque */}
        {!isTv && (
          <div className="grid gap-2">
            <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
              3 · Rival
            </span>
            {!isAttack ? (
              <Select disabled value={null} items={{}}>
                <SelectTrigger className="w-70" aria-label="Rival">
                  <SelectValue placeholder="Só no ataque ao rival" />
                </SelectTrigger>
              </Select>
            ) : campaign.rivals.length === 0 ? (
              <span className="text-[13px] text-muted-foreground">
                Sem rival: o {campaign.party_abbr} é o único partido na eleição.
              </span>
            ) : (
              <Select
                value={rivalId === null ? null : String(rivalId)}
                items={Object.fromEntries(campaign.rivals.map((item) => [String(item.party_id), item.abbr]))}
                onValueChange={(value) => value && onRival(Number(value))}
              >
                <SelectTrigger className="w-70" aria-label="Rival">
                  <SelectValue placeholder="Escolha o rival" />
                </SelectTrigger>
                <SelectContent>
                  {campaign.rivals.map((item) => (
                    <SelectItem key={item.party_id} value={String(item.party_id)}>
                      <PartyMark abbr={item.abbr} color={item.color} size="sm" />
                      {item.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        )}
      </div>

      {/* Resumo do dado */}
      <div className="grid content-start gap-3.5 rounded-[10px] border bg-subtle p-4">
        <div className="grid gap-0.5">
          <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">Resumo</span>
          <b className="text-base">{summaryTitle(kind, group, rival?.abbr ?? null)}</b>
          <span className="text-[12.5px] text-muted-foreground">
            {isTv
              ? "Todos os grupos, pelo peso do eleitorado"
              : isAttack && rival
                ? `${displayPercent(weights.get(group) ?? 0, 0)} do eleitorado · o apoio do ${rival.abbr} fica só com o ${rival.abbr}`
                : `${displayPercent(weights.get(group) ?? 0, 0)} do eleitorado · apoio ${Math.round(Number(target?.support ?? 0))}, rejeição ${Math.round(Number(target?.rejection ?? 0))}`}
          </span>
        </div>

        {target && <SummaryBody campaign={campaign} kind={kind} group={group} target={target} rival={rival?.abbr} />}

        <div className="grid gap-1.5 border-t pt-3">
          <Button size="lg" className="w-full" disabled={!ready} onClick={onRoll}>
            <Dices />
            Rolar o dado · {displayMoney(price)}
          </Button>
          <span className="text-center text-[11.5px] text-faint-foreground">
            {short > 0
              ? `Faltam ${displayMoney(short)} no seu caixa`
              : isAttack && rivalId === null
                ? "Escolha o rival para rolar"
                : cash === null
                  ? "Sai da sua carteira"
                  : `Sai da sua carteira: ${displayMoney(cash)} → ${displayMoney(cash - price)}`}
          </span>
        </div>
      </div>
    </div>
  );
}

/** A TV não escolhe grupo: o ganho vai a todos, na proporção do peso de cada um. */
function TvReach({ weights }: { weights: Map<VoterGroup, string> }) {
  const rows = [...weights].sort((a, b) => Number(b[1]) - Number(a[1]));
  const top = Number(rows[0]?.[1] ?? 1);

  return (
    <div className="grid gap-3 rounded-[10px] border bg-subtle p-4">
      <div className="flex items-center gap-2.5 text-sm font-semibold">
        <ActionIcon kind="TV" />
        Atinge todos os grupos, pelo peso de cada um
      </div>
      <div className="grid gap-2">
        {rows.map(([group, weight]) => (
          <div key={group} className="grid grid-cols-[190px_minmax(0,1fr)_36px] items-center gap-2.5 text-[12.5px]">
            <span className="truncate">{GROUP_INFO[group].label}</span>
            <Progress value={(Number(weight) / top) * 100} size="sm" aria-label={GROUP_INFO[group].label} />
            <span className="text-right font-mono">{displayPercent(weight, 0)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

type ActionChoiceProps = {
  action: CampaignAction;
  selected: boolean;
  short: number;
  cash: number | null;
  noRival: boolean;
  partyAbbr: string;
  onSelect: () => void;
};

function ActionChoice({ action, selected, short, cash, noRival, partyAbbr, onSelect }: ActionChoiceProps) {
  const info = ACTION_INFO[action.action];
  const disabled = short > 0 || noRival;
  // O efeito médio da ação no melhor grupo, antes de escolher o grupo
  const best = action.targets.reduce(
    (top, target) => (Math.abs(Number(target.average)) > Math.abs(top) ? Number(target.average) : top),
    0,
  );
  const preview =
    action.action === "TV"
      ? `${signed(best, 1)} em cada grupo`
      : action.action === "ATTACK"
        ? `${signed(best, 1)} do rival`
        : action.action === "EVENT"
          ? `${signed(best, 1)} e repara a rejeição`
          : signed(best, 1);

  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      disabled={disabled}
      onClick={onSelect}
      className={cn(
        "relative grid content-start gap-1.5 rounded-[10px] border bg-card p-3 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        selected && "border-primary bg-info-soft/40 ring-1 ring-primary",
        disabled && "bg-subtle",
      )}
    >
      <div className={cn("grid gap-1.5", disabled && "opacity-60")}>
        <div className="flex items-center justify-between">
          <ActionIcon kind={action.action} />
          <span className="font-mono text-[13px] font-semibold">{displayMoney(action.price)}</span>
        </div>
        <b className="text-sm">{info.label}</b>
        <span className="text-xs leading-snug text-muted-foreground">{info.blurb}</span>
        <div className="grid gap-0.5 border-t pt-1.5">
          <span className="font-mono text-xs font-semibold text-success">em média {preview}</span>
          <span className="text-[11px] text-faint-foreground">{info.dice}</span>
        </div>
      </div>
      {short > 0 && (
        <span className="text-xs text-destructive">
          Faltam {displayMoney(short)} no seu caixa{cash !== null && ` (${displayMoney(cash)})`}
        </span>
      )}
      {noRival && (
        <span className="text-xs text-muted-foreground">Sem rival: o {partyAbbr} é o único partido na eleição</span>
      )}
    </button>
  );
}

type GroupChoicesProps = {
  action: CampaignAction;
  kind: CampaignActionKind;
  group: VoterGroup;
  onGroup: (group: VoterGroup) => void;
  weights: Map<VoterGroup, string>;
  undecided: Map<VoterGroup, string | null> | null;
  today: string;
};

const GROUP_ROW = "grid grid-cols-[16px_28px_minmax(0,1fr)_54px_64px_92px_74px] items-center gap-3";

function GroupChoices({ action, kind, group, onGroup, weights, undecided, today }: GroupChoicesProps) {
  return (
    <div role="radiogroup" aria-label="Grupo" className="grid gap-0.5">
      <div
        className={cn(
          GROUP_ROW,
          "px-2 pb-0.5 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase",
        )}
      >
        <span />
        <span />
        <span>Grupo</span>
        <span className="text-right">{undecided ? "Voto" : "Apoio"}</span>
        <span className="text-right">{undecided ? "Indecisos" : "Rejeição"}</span>
        <span>
          {ACTION_INFO[kind].plural}
          {undecided ? " no 2º turno" : ` em ${monthLabel(today)}`}
        </span>
        <span className="text-right">Rende</span>
      </div>
      {action.targets.map((target) => {
        if (target.group === null) return null;
        const selected = target.group === group;
        const rate = Number(target.rate);
        return (
          <button
            key={target.group}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onGroup(target.group!)}
            className={cn(
              GROUP_ROW,
              "rounded-lg border border-transparent px-2 py-1.5 text-left text-[13px] outline-none hover:bg-subtle focus-visible:ring-3 focus-visible:ring-ring/50",
              selected && "border-primary bg-info-soft/40",
            )}
          >
            <span
              aria-hidden
              className={cn(
                "size-4 rounded-full border-2 border-input",
                selected && "border-primary bg-primary shadow-[inset_0_0_0_3px_var(--card)]",
              )}
            />
            <GroupIcon group={target.group} className="size-7" />
            <span className="grid min-w-0">
              <span className={cn("truncate", selected ? "font-semibold" : "font-medium")}>
                {GROUP_INFO[target.group].label}
              </span>
              <span className="text-[11px] text-faint-foreground">
                {displayPercent(weights.get(target.group) ?? 0, 0)} do eleitorado
              </span>
            </span>
            <span className="text-right font-mono">{Math.round(Number(target.support ?? 0))}</span>
            <span className="text-right font-mono">
              {undecided
                ? Math.round(Number(undecided.get(target.group) ?? 0))
                : Math.round(Number(target.rejection ?? 0))}
            </span>
            <span className="flex items-center gap-1.5">
              <span className="flex gap-0.5" aria-hidden>
                {[0, 1, 2].map((pip) => (
                  <i
                    key={pip}
                    className={cn(
                      "size-2 rounded-full not-italic",
                      pip < target.uses_this_month ? "bg-primary" : "bg-border",
                    )}
                  />
                ))}
              </span>
              <span className="text-[11px] text-faint-foreground">{target.uses_this_month}×</span>
            </span>
            <span
              className={cn(
                "text-right font-mono font-semibold",
                rate >= 1 ? "text-success" : rate >= 0.5 ? "text-warning" : "text-destructive",
              )}
            >
              <Tooltip>
                <TooltipTrigger render={<span className="cursor-help" />}>
                  <span className="underline decoration-dotted">{ratePercent(rate)}</span>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-80">
                  Retorno decrescente: a mesma ação no mesmo grupo rende 100%, 50% e 25% no mês. O partido já fez{" "}
                  {target.uses_this_month}× aqui neste mês; em {nextMonthLabel(today)} volta a 100%.
                </TooltipContent>
              </Tooltip>
            </span>
          </button>
        );
      })}
    </div>
  );
}

type SummaryBodyProps = {
  campaign: CampaignPanel;
  kind: CampaignActionKind;
  group: VoterGroup;
  target: CampaignTarget;
  rival: string | undefined;
};

/** A tabela de faixas do resumo e as linhas de média, reparo e valor no dia da eleição. */
function SummaryBody({ campaign, kind, group, target, rival }: SummaryBodyProps) {
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
          <span className="text-right text-[11px] text-faint-foreground">
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
            {chancePercent(disaster.chance)} · {bandEffect(disaster)}
          </SummaryRow>
        )}
        {kind === "ATTACK" && disaster && (
          <>
            <SummaryRow label="Sai pela culatra" tone="down">
              {chancePercent(disaster.chance)} · {signed(disaster.rejection)} de rejeição a você
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

function SummaryRow({ label, tone, children }: { label: string; tone?: "up" | "down"; children: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={cn(
          "text-right font-mono font-semibold",
          tone === "up" && "text-success",
          tone === "down" && "text-destructive",
        )}
      >
        {children}
      </span>
    </div>
  );
}
