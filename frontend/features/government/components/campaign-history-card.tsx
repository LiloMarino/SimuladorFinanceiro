import { useState } from "react";
import { Newspaper } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { Kpi } from "@/shared/components/kpi";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { CampaignEntry, CampaignPanel, ElectionParty } from "@/types";
import { useCampaignHistory } from "../hooks/queries/useCampaignHistory";
import { BAND_INFO, effectText, entryTitle, signed } from "../lib/campaign";
import { GROUP_INFO } from "../lib/voters";
import { D20 } from "./campaign-dice";
import { PartyMark } from "./party-mark";
import { GroupIcon } from "./value-chip";

const PAGE = 10;

type Kind = "all" | "actions" | "base" | "received";
type Who = "all" | "me";

const KIND_LABEL: Record<Kind, string> = {
  all: "Tudo",
  actions: "Ações",
  base: "Verba",
  received: "Ataques recebidos",
};

const matchesKind = (entry: CampaignEntry, kind: Kind) =>
  kind === "all" ||
  (kind === "actions" && entry.kind !== "BASE_BUDGET" && entry.kind !== "ATTACK_RECEIVED") ||
  (kind === "base" && entry.kind === "BASE_BUDGET") ||
  (kind === "received" && entry.kind === "ATTACK_RECEIVED");

type CampaignHistoryCardProps = {
  campaign: CampaignPanel;
  party: ElectionParty;
  nickname: string;
};

/** Cada ação dos filiados, a verba de base e os ataques recebidos, com quanto cada um vale hoje depois da queda. */
export function CampaignHistoryCard({ campaign, party, nickname }: CampaignHistoryCardProps) {
  const { data, error, refetch } = useCampaignHistory();
  const [kind, setKind] = useState<Kind>("all");
  const [who, setWho] = useState<Who>("all");
  const [shown, setShown] = useState(PAGE);

  const entries = (data?.entries ?? []).filter(
    (entry) => matchesKind(entry, kind) && (who === "all" || entry.nickname === nickname),
  );

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          {/* Cabeçalho */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Campanha do {party.abbr} · histórico</h2>
              <span className="text-[13px] text-muted-foreground">
                Cada ação dos filiados, a verba de base e os ataques que o {party.abbr} recebeu. Só os filiados do{" "}
                {party.abbr} veem.
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              <ToggleGroup
                variant="segmented"
                aria-label="Tipo de linha"
                value={[kind]}
                onValueChange={(values) => {
                  if (values[0]) {
                    setKind(values[0] as Kind);
                    setShown(PAGE);
                  }
                }}
              >
                {(Object.keys(KIND_LABEL) as Kind[]).map((value) => (
                  <ToggleGroupItem key={value} value={value}>
                    {KIND_LABEL[value]}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
              <ToggleGroup
                variant="segmented"
                aria-label="Quem fez"
                value={[who]}
                onValueChange={(values) => {
                  if (values[0]) {
                    setWho(values[0] as Who);
                    setShown(PAGE);
                  }
                }}
              >
                <ToggleGroupItem value="all">Todos os filiados</ToggleGroupItem>
                <ToggleGroupItem value="me">Só eu</ToggleGroupItem>
              </ToggleGroup>
            </div>
          </div>

          {/* Totais e o apoio de campanha de hoje em cada grupo */}
          <div className="grid items-start gap-6 md:grid-cols-[200px_minmax(0,1fr)]">
            <div className="grid gap-4">
              <Kpi
                label="Gasto em ações"
                value={displayMoney(campaign.actions_spent)}
                note={`${campaign.actions_count} ${campaign.actions_count === 1 ? "ação" : "ações"} na campanha`}
              />
              <Kpi
                label="Verba de base"
                value={displayMoney(campaign.base_spent)}
                note={`${campaign.base_charges} ${campaign.base_charges === 1 ? "cobrança mensal" : "cobranças mensais"}`}
              />
            </div>
            <div className="grid gap-2">
              <span className="text-xs font-medium text-muted-foreground">
                O que a campanha soma hoje ao apoio do {party.abbr} em cada grupo, já com a queda
              </span>
              <div className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-3">
                {campaign.groups.map((item) => (
                  <div key={item.group} className="grid min-w-0 gap-1.5 rounded-[10px] border px-3 py-2.5">
                    <span className="flex min-w-0 items-center gap-2 text-[12.5px]">
                      <GroupIcon group={item.group} className="size-7" />
                      <span className="truncate">{GROUP_INFO[item.group].label}</span>
                    </span>
                    <span
                      className={cn(
                        "font-mono text-lg font-semibold",
                        Number(item.campaign) < 0 ? "text-destructive" : "text-success",
                      )}
                    >
                      {signed(item.campaign, 1)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Linhas */}
          {error ? (
            <div className="flex items-center justify-between gap-3 rounded-lg bg-destructive-soft px-3.5 py-2.5 text-sm">
              <span>Não deu para carregar o histórico.</span>
              <Button size="sm" variant="outline" onClick={() => void refetch()}>
                Tentar de novo
              </Button>
            </div>
          ) : !data ? (
            <div className="grid gap-2" aria-busy="true" aria-label="Carregando o histórico">
              {Array.from({ length: 4 }, (_, index) => (
                <Skeleton key={index} className="h-8" />
              ))}
            </div>
          ) : entries.length === 0 ? (
            <p className="rounded-lg border border-dashed px-3 py-6 text-center text-[13px] text-muted-foreground">
              {data.entries.length === 0 ? "Nenhuma ação ainda." : "Nenhuma linha com esses filtros."}
            </p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Quem</TableHead>
                    <TableHead>Ação</TableHead>
                    <TableHead>Grupo</TableHead>
                    <TableHead>Dado</TableHead>
                    <TableHead className="text-right">Efeito no dia</TableHead>
                    <TableHead className="text-right">Vale hoje</TableHead>
                    <TableHead className="text-right">Pago</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entries.slice(0, shown).map((entry) => (
                    <HistoryRow key={`${entry.kind}-${entry.id}`} entry={entry} party={party} />
                  ))}
                </TableBody>
              </Table>
              <div className="flex items-center justify-between gap-3">
                <span className="text-[12.5px] text-muted-foreground">
                  Mostrando {Math.min(shown, entries.length)} de {entries.length}
                </span>
                {shown < entries.length && (
                  <Button variant="outline" size="sm" onClick={() => setShown(shown + PAGE)}>
                    Carregar mais
                  </Button>
                )}
              </div>
            </>
          )}

          <p className="rounded-lg bg-subtle px-2.5 py-2 text-[12.5px] leading-relaxed text-muted-foreground">
            Por que “vale hoje” é menor: o apoio da campanha, das ações e da verba, cai pela metade a cada 3 meses. No
            dia da eleição pesam sobretudo os últimos meses.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function HistoryRow({ entry, party }: { entry: CampaignEntry; party: ElectionParty }) {
  const member = party.members.find((candidate) => candidate.nickname === entry.nickname);
  const received = entry.kind === "ATTACK_RECEIVED";
  const base = entry.kind === "BASE_BUDGET";
  const worth = Number(entry.worth_now);
  const share = `${Math.round(Number(entry.worth_share) * 100)}%`;

  return (
    <TableRow variant={received ? "warning" : "default"}>
      <TableCell>
        <span className="font-mono text-muted-foreground">{displayDayMonth(entry.date)}</span>
      </TableCell>
      <TableCell>
        {received ? (
          <span className="flex items-center gap-2">
            atacou
            <PartyMark abbr={entry.party_abbr} color={entry.party_color} size="sm" />
          </span>
        ) : base ? (
          <span className="flex items-center gap-2">
            filiados
            <PartyMark abbr={entry.party_abbr} color={entry.party_color} size="sm" />
          </span>
        ) : entry.nickname ? (
          <span className="flex items-center gap-2">
            {entry.nickname}
            <PlayerAvatar nickname={entry.nickname} color={member?.color} size="sm" />
          </span>
        ) : (
          <span className="text-muted-foreground">computador</span>
        )}
      </TableCell>
      <TableCell>
        <span className="flex items-center gap-1.5">
          {entryTitle(entry)}
          {entry.newsworthy && (
            <Badge variant="secondary" size="sm">
              <Newspaper />
              jornal
            </Badge>
          )}
        </span>
      </TableCell>
      <TableCell>
        {entry.group ? (
          <span className="flex items-center gap-2">
            {GROUP_INFO[entry.group].label}
            <GroupIcon group={entry.group} className="size-7" />
          </span>
        ) : (
          <span className="text-muted-foreground">Todos os grupos</span>
        )}
      </TableCell>
      <TableCell>
        {entry.band && entry.roll !== null ? (
          <span className="flex items-center gap-1.5">
            {entry.rolls.map((value, index) => (
              <D20
                key={index}
                value={value}
                band={entry.band}
                size={26}
                dim={entry.rolls.length > 1 && value !== entry.roll}
              />
            ))}
            <Badge variant={BAND_INFO[entry.band].badge} size="sm">
              {BAND_INFO[entry.band].label}
            </Badge>
          </span>
        ) : received ? (
          <span className="text-xs text-muted-foreground">rolado pelo {entry.party_abbr}</span>
        ) : (
          <span className="text-xs text-faint-foreground">sem dado</span>
        )}
      </TableCell>
      <TableCell className="text-right">
        <span
          className={cn(
            "font-mono",
            received || worth < 0
              ? "text-destructive"
              : entry.kind === "ATTACK"
                ? "text-muted-foreground"
                : "text-success",
          )}
        >
          {effectText(entry)}
        </span>
      </TableCell>
      <TableCell className="text-right">
        <div className="grid justify-items-end font-mono">
          <span
            className={cn(
              worth < 0 ? "text-destructive" : entry.kind === "ATTACK" ? "text-muted-foreground" : "text-success",
            )}
          >
            {entry.kind === "ATTACK" ? `${entry.rival_abbr} ${signed(worth, 1)}` : signed(worth, 1)}
          </span>
          <span className="text-[11px] text-faint-foreground">{share}</span>
        </div>
      </TableCell>
      <TableCell className="text-right">
        <span className="font-mono">{entry.price === null ? "—" : displayMoney(entry.price)}</span>
      </TableCell>
    </TableRow>
  );
}
