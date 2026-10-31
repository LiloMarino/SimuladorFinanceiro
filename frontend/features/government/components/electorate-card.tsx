import { useState } from "react";
import { LayoutGrid, List } from "lucide-react";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty, ElectionPoll, ElectorateRow, VoterGroupInfo } from "@/types";
import { campaignEnded } from "../lib/election";
import { BALANCE, REJECTION, SUPPORT } from "../lib/election-metrics";
import {
  GROUP_INFO,
  READING_LABEL,
  type GroupSort,
  marginRange,
  nextPollDate,
  partyOrder,
  pollPercent,
  pollPoints,
  signedPoints,
  sortElectorate,
  topWants,
} from "../lib/voters";
import { GroupPollBar } from "./group-poll-bar";
import { PollLegend } from "./poll-legend";
import { GroupIcon, ValueChip } from "./value-chip";

type View = "cards" | "table";

type ElectorateCardProps = {
  panel: ElectionPanel;
  /** O partido de quem vê: só os filiados recebem o apoio e a rejeição exatos */
  party: ElectionParty;
};

/** O partido de quem vê em cada grupo de eleitores: apoio, rejeição, saldo e a pesquisa no grupo. */
export function ElectorateCard({ panel, party }: ElectorateCardProps) {
  const [view, setView] = useState<View>("cards");
  const [sort, setSort] = useState<GroupSort>("weight");
  const groups = new Map(panel.groups.map((group) => [group.group, group]));
  const latest = panel.polls.at(-1);
  const groupPolls = new Map(latest?.groups.map((poll) => [poll.group, poll]));
  const parties = partyOrder(panel.parties);
  const rows = sortElectorate(panel.electorate, panel.groups, sort).flatMap((row) => {
    const group = groups.get(row.group);
    return group ? [{ row, group, poll: groupPolls.get(row.group) }] : [];
  });

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          {/* Cabeçalho */}
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Eleitorado · o {party.abbr} em cada grupo</h2>
              <span className="inline-flex items-center gap-1 text-[13px] text-muted-foreground">
                O número no canto é o saldo, apoio menos rejeição: é dele que sai o voto. Borda vermelha: a rejeição
                passa o apoio, e o {party.abbr} não tem voto ali.
                <MetricHint metric={BALANCE} />
              </span>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <Badge variant="secondary">Só o seu partido vê apoio e rejeição</Badge>
              <ToggleGroup
                variant="segmented"
                aria-label="Ver o eleitorado como"
                value={[view]}
                onValueChange={(values) => values[0] && setView(values[0] as View)}
              >
                <ToggleGroupItem value="cards">
                  <LayoutGrid />
                  Cartões
                </ToggleGroupItem>
                <ToggleGroupItem value="table">
                  <List />
                  Tabela
                </ToggleGroupItem>
              </ToggleGroup>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <PollLegend parties={parties} />
            <ToggleGroup
              variant="segmented"
              aria-label="Ordenar os grupos"
              value={[sort]}
              onValueChange={(values) => values[0] && setSort(values[0] as GroupSort)}
            >
              <ToggleGroupItem value="weight">Por peso</ToggleGroupItem>
              <ToggleGroupItem value="balance">Por saldo</ToggleGroupItem>
            </ToggleGroup>
          </div>

          {!latest && (
            <span className="text-xs text-muted-foreground">
              {campaignEnded(panel.phase)
                ? `Campanha encerrada, sem pesquisa. Os grupos mostram onde o ${party.abbr} começou.`
                : `A primeira pesquisa sai em ${displayShortDate(nextPollDate(panel.today))}. Até lá, os grupos mostram onde o ${party.abbr} começa.`}
            </span>
          )}

          {/* Grupos */}
          {view === "cards" ? (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {rows.map(({ row, group, poll }) => (
                <GroupCard key={row.group} row={row} group={group} poll={poll} party={party} parties={parties} />
              ))}
            </div>
          ) : (
            <ElectorateTable rows={rows} party={party} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

type GroupPoll = ElectionPoll["groups"][number];
type GroupRow = { row: ElectorateRow; group: VoterGroupInfo; poll: GroupPoll | undefined };

type GroupCardProps = GroupRow & { party: ElectionParty; parties: ElectionParty[] };

function GroupCard({ row, group, poll, party, parties }: GroupCardProps) {
  const support = Number(row.support);
  const rejection = Number(row.rejection);
  const balance = support - rejection;
  const label = GROUP_INFO[row.group].label;
  const weight = displayPercent(group.weight, 0);
  const own = poll ? (pollPoints(poll.entries).get(party.id) ?? 0) : null;

  return (
    <div
      className={cn(
        "grid content-start gap-3 rounded-lg border bg-card p-3.5",
        rejection > support && "border-destructive/30",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2.5">
          <GroupIcon group={row.group} />
          <div className="grid min-w-0 gap-px">
            <b className="truncate text-sm font-semibold">{label}</b>
            <span className="text-xs text-muted-foreground">{weight} do eleitorado</span>
          </div>
        </div>
        <span
          className={cn(
            "font-mono text-[13px] font-semibold",
            balance > 0 ? "text-success" : balance < 0 ? "text-destructive" : "text-muted-foreground",
          )}
        >
          {signedPoints(balance)}
        </span>
      </div>

      <div className="flex flex-wrap gap-1">
        {topWants(group).map((value) => (
          <ValueChip key={value} value={value} />
        ))}
      </div>

      <div className="grid gap-2">
        <MeterRow label="Apoio" value={support} change={row.support_change} tone="success" goodWhenUp />
        <MeterRow label="Rejeição" value={rejection} change={row.rejection_change} tone="destructive" />
        {rejection === 0 && <span className="text-xs text-muted-foreground">Rejeição: ninguém rejeita ainda</span>}
      </div>

      <div className="grid gap-1.5 border-t pt-2.5">
        <div className="flex justify-between text-xs">
          <span className="text-muted-foreground">Pesquisa no grupo</span>
          {poll && own !== null ? (
            <span className="font-mono">
              <b style={{ color: party.color ?? undefined }}>
                {party.abbr} {pollPercent(own, poll.margin)}
              </b>
              {poll.margin > 0 && <span className="text-faint-foreground"> ±{poll.margin}</span>}
            </span>
          ) : (
            <span className="text-faint-foreground">ainda sem pesquisa</span>
          )}
        </div>
        {poll && <GroupPollBar poll={poll} parties={parties} title={`${label} · ${weight} do eleitorado`} />}
        <span className="text-xs text-muted-foreground">
          Lê: {group.readings.map((reading) => READING_LABEL[reading]).join(", ")}
        </span>
      </div>
    </div>
  );
}

type MeterRowProps = {
  label: string;
  value: number;
  change: string | null;
  tone: "success" | "destructive";
  /** Apoio subir é bom; rejeição subir é ruim */
  goodWhenUp?: boolean;
};

function MeterRow({ label, value, change, tone, goodWhenUp = false }: MeterRowProps) {
  return (
    <div className="grid grid-cols-[62px_1fr_26px_36px] items-center gap-2 text-xs">
      <span className="text-muted-foreground">{label}</span>
      <Progress value={value} size="sm" indicatorTone={tone} aria-label={label} />
      <span className="text-right font-mono font-semibold">{Math.round(value)}</span>
      <Change value={change} goodWhenUp={goodWhenUp} />
    </div>
  );
}

/** A mudança desde a pesquisa anterior: ▲ ou ▼ na cor de bom ou ruim, ou um traço sem mudança. */
function Change({ value, goodWhenUp }: { value: string | null; goodWhenUp: boolean }) {
  const change = Math.round(Number(value ?? 0));
  if (change === 0) return <span className="font-mono text-faint-foreground">—</span>;
  const good = change > 0 === goodWhenUp;
  return (
    <span className={cn("font-mono", good ? "text-success" : "text-destructive")}>
      {change > 0 ? "▲" : "▼"} {Math.abs(change)}
    </span>
  );
}

function ElectorateTable({ rows, party }: { rows: GroupRow[]; party: ElectionParty }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Grupo</TableHead>
          <TableHead>O que quer</TableHead>
          <TableHead>
            <MetricLabel metric={{ ...SUPPORT, label: `Apoio ao ${party.abbr}` }} />
          </TableHead>
          <TableHead>
            <MetricLabel metric={{ ...REJECTION, label: `Rejeição ao ${party.abbr}` }} />
          </TableHead>
          <TableHead className="text-right">{party.abbr} na pesquisa</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(({ row, group, poll }) => {
          const own = poll ? (pollPoints(poll.entries).get(party.id) ?? 0) : null;
          const [low, high] = poll && own !== null ? marginRange(own, poll.margin) : [0, 0];
          return (
            <TableRow key={row.group}>
              <TableCell>
                <div className="flex items-center gap-2.5">
                  <GroupIcon group={row.group} />
                  <div className="grid min-w-0 gap-px">
                    <b className="text-sm font-semibold">{GROUP_INFO[row.group].label}</b>
                    <span className="text-xs text-muted-foreground">
                      {displayPercent(group.weight, 0)} do eleitorado
                    </span>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {topWants(group).map((value) => (
                    <ValueChip key={value} value={value} />
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <TableMeter value={Number(row.support)} change={row.support_change} tone="success" goodWhenUp />
              </TableCell>
              <TableCell>
                <TableMeter value={Number(row.rejection)} change={row.rejection_change} tone="destructive" />
                {Number(row.rejection) === 0 && (
                  <span className="text-xs text-muted-foreground">ninguém rejeita ainda</span>
                )}
              </TableCell>
              <TableCell className="text-right">
                {poll && own !== null ? (
                  <div className="grid justify-items-end gap-0.5">
                    <span className="font-mono font-semibold">
                      {pollPercent(own, poll.margin)}
                      {poll.margin > 0 && <span className="font-normal text-faint-foreground"> ±{poll.margin}</span>}
                    </span>
                    {poll.margin > 0 && (
                      <span className="text-xs text-muted-foreground">
                        entre {pollPercent(low, poll.margin)} e {pollPercent(high, poll.margin)}
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="text-faint-foreground">—</span>
                )}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

function TableMeter({ value, change, tone, goodWhenUp = false }: Omit<MeterRowProps, "label">) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-6 font-mono text-[15px] font-semibold">{Math.round(value)}</span>
      <Progress value={value} size="sm" indicatorTone={tone} className="w-14" />
      <Change value={change} goodWhenUp={goodWhenUp} />
    </div>
  );
}
