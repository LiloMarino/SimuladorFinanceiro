import { PartyMark, PersonMark } from "@/shared/components/party-mark";
import { PartyMarkPair } from "@/shared/components/party-mark-pair";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ValueChips } from "@/shared/components/value-chip";
import { displayMoneyWhole, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionParty, Federation } from "@/types";
import type { RaceRow } from "../lib/federation";
import { pollPercent } from "../lib/voters";

type FederationTileProps = {
  /** A linha da corrida com a federação e os dois partidos, o do candidato primeiro */
  row: RaceRow & { federation: Federation };
  current: boolean;
  margin: number;
};

/** O cartão da federação no lugar dos dois partidos: a chapa, a soma na pesquisa e a fatia de cada partido. */
export function FederationTile({ row, current, margin }: FederationTileProps) {
  const { federation, parties } = row;
  const [leader] = parties;
  if (!leader) return null;
  const orienting = parties.find((party) => party.id === federation.orienting_party_id);
  const total = parties.reduce((sum, party) => sum + Number(party.intention_points), 0);

  return (
    <Card variant={current ? "info" : "default"} className="h-full">
      <CardContent className="h-full">
        <div className="flex h-full flex-col gap-3.5">
          {/* Nome e chapa */}
          <div className="grid gap-1.5">
            <div className="flex items-center gap-2">
              <PartyMarkPair parties={parties} size="md" />
              <b className="min-w-0 flex-1 text-[15px] font-semibold">{federation.name}</b>
              {current && <Badge variant="info">Seu partido</Badge>}
            </div>
            <span className="flex flex-wrap items-center gap-1.5 text-[13px] text-muted-foreground">
              {leader.candidate && <PersonMark person={leader.candidate} />}
              Candidato: ({leader.abbr}) {federation.candidate}
              {leader.vice && <span>· vice: {leader.vice.name}</span>}
            </span>
            <span>
              <Badge variant="federation">Federação até {displayShortDate(federation.ends_on)}</Badge>
            </span>
          </div>

          {/* Contas da federação */}
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2.5 rounded-lg bg-subtle px-3.5 py-3">
            <Stat label="Intenção de voto">
              <span className="font-mono">{pollPercent(total, margin)}</span>
              {margin > 0 && <span className="font-mono text-xs font-normal text-muted-foreground">±{margin}</span>}
            </Stat>
            <Stat label="Orientação">
              <span>do {orienting?.abbr}</span>
              <span className="text-xs font-normal text-muted-foreground">mais cadeiras</span>
            </Stat>
            <Stat label="Rejeição herdada">
              <span className="text-xs font-normal">½ da do parceiro</span>
            </Stat>
            <Stat label="Verba">
              <span className="text-xs font-normal">cada um a sua</span>
            </Stat>
          </dl>

          {/* Partidos da federação */}
          <div className="grid gap-2">
            <span className="text-xs font-medium text-muted-foreground">Partidos da federação</span>
            {parties.map((party) => (
              <PartyLine key={party.id} party={party} />
            ))}
          </div>

          <span className="mt-auto text-xs text-muted-foreground">
            Promessas da chapa: {leader.promises.length === 0 ? "ainda nenhuma" : `as ${leader.promises.length}`} do{" "}
            {leader.abbr}. Formada em {displayShortDate(federation.formed_on)}.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

function PartyLine({ party }: { party: ElectionParty }) {
  return (
    <div className="grid gap-1.5 rounded-lg border px-3 py-2">
      <div className="flex items-center gap-2 text-[13px]">
        <PartyMark abbr={party.abbr} color={party.color} size="sm" />
        <b className="min-w-0 flex-1 font-medium">{party.name}</b>
        <span className="font-mono">{displayPercent(Number(party.intention_points) / 100, 1)}</span>
        <span className="font-mono text-xs text-muted-foreground">{displayMoneyWhole(party.budget)}</span>
      </div>
      <ValueChips values={party.flags} />
    </div>
  );
}

function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-0.5">
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="flex min-h-6 items-center gap-1 font-semibold">{children}</dd>
    </div>
  );
}
