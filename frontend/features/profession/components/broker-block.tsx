import { Link } from "react-router-dom";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import {
  displayMoney,
  displayMoneyLarge,
  displayMonthName,
  displayMonthYear,
  displayPercent,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { BROKER_COMMISSION, HOUSE_SCOREBOARD, TARGET_PRICE } from "../lib/profession-metrics";
import { FigureCard } from "./figure-card";
import { BlockBand, MechanicBlock } from "./mechanic-block";

type BrokerMechanic = Extract<ProfessionMechanic, { kind: "broker" }>;
type HouseReport = NonNullable<BrokerMechanic["current"]>;
type Recommendation = HouseReport["items"][number];
type BrokerBlockProps = { mechanic: BrokerMechanic };

const SCOREBOARD_NOTE = "só conta recomendação com o prazo vencido · o acaso daria 50%";

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

/** "Sua mecânica: relatório da casa" do Corretor: as recomendações do mês, o placar da casa e a comissão sobre o volume da sala. */
export function BrokerBlock({ mechanic }: BrokerBlockProps) {
  const { current } = mechanic;

  if (!current) {
    return (
      <MechanicBlock
        title="Sua mecânica: relatório da casa"
        description="O primeiro relatório chega no 5º dia útil do mês."
        status={mechanic.status}
      >
        <BeforeFirstReport mechanic={mechanic} />
      </MechanicBlock>
    );
  }

  return (
    <MechanicBlock
      title="Sua mecânica: relatório da casa"
      description={`A corretora manda as recomendações de ${displayMonthName(current.month)} dias antes das notícias. Acerta mais que o acaso, mas erra.`}
      status={mechanic.status}
      action={
        <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/variable-income" />}>
          Abrir na Renda variável
        </Button>
      }
      links={[{ label: "Renda variável, ação com o selo do relatório", to: "/variable-income" }]}
    >
      <Figures mechanic={mechanic} />
      <CurrentReport report={current} />
      {mechanic.previous && <PreviousReport report={mechanic.previous} />}
    </MechanicBlock>
  );
}

/** Os três números do bloco: o placar da casa, a renda do mês e a comissão. */
function Figures({ mechanic }: BrokerBlockProps) {
  const scoreboard =
    mechanic.hit_rate === null
      ? "—"
      : `Acertou ${mechanic.hits} de ${mechanic.resolved} (${displayPercent(mechanic.hit_rate, 0)})`;
  const share = `${displayPercent(mechanic.commission_rate)} dos ${displayMoneyLarge(mechanic.volume)} negociados na sala, ÷ ${mechanic.brokers} ${mechanic.brokers === 1 ? "corretor" : "corretores"}`;

  return (
    <div className="grid gap-3 md:grid-cols-3">
      <FigureCard
        label={
          <span className="inline-flex items-center gap-1">
            Placar da casa <MetricHint metric={HOUSE_SCOREBOARD} />
          </span>
        }
        value={scoreboard}
        note={SCOREBOARD_NOTE}
      />
      <FigureCard
        label="Renda do mês"
        value={displayMoney(mechanic.income)}
        note={`fixo ${displayMoney(mechanic.fixed_income)} + comissão ${displayMoney(mechanic.commission)}`}
      />
      <FigureCard
        label={
          <span className="inline-flex items-center gap-1">
            Comissão <MetricHint metric={BROKER_COMMISSION} />
          </span>
        }
        value={displayMoney(mechanic.commission)}
        note={mechanic.capped ? `${share} · limitada ao teto de 1× o fixo` : share}
      />
    </div>
  );
}

/** O lado da recomendação da casa, em selo. */
function SideBadge({ side }: { side: Recommendation["side"] }) {
  return (
    <Badge variant={side === "buy" ? "success" : "destructive"} size="tag">
      {side === "buy" ? "Compra" : "Venda"}
    </Badge>
  );
}

/** O relatório vigente: ação, lado, preço de hoje, alvo e prazo de cada recomendação. */
function CurrentReport({ report }: { report: HouseReport }) {
  return (
    <div className="grid gap-2">
      <h3 className="text-sm font-semibold">
        Relatório de {displayMonthName(report.month)} · recebido em {displayShortDate(report.issued_on)}
      </h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Ação</TableHead>
            <TableHead>Recomendação</TableHead>
            <TableHead numeric>Hoje</TableHead>
            <TableHead numeric>
              <span className="inline-flex items-center gap-1">
                Preço-alvo <MetricHint metric={TARGET_PRICE} />
              </span>
            </TableHead>
            <TableHead numeric>Prazo</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.items.map((item) => (
            <TableRow key={item.id}>
              <TableCell>{item.ticker}</TableCell>
              <TableCell>
                <SideBadge side={item.side} />
              </TableCell>
              <TableCell numeric>{displayMoney(item.price)}</TableCell>
              <TableCell numeric>{displayMoney(item.target)}</TableCell>
              <TableCell numeric>{displayMonthYear(item.deadline)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

/** O desfecho de uma recomendação: o selo do resultado e, ao lado, o preço que o decidiu ou o prazo que falta. */
function Outcome({ item }: { item: Recommendation }) {
  const [variant, label, detail] =
    item.result === "hit"
      ? (["success", "Acertou", `chegou a ${displayMoney(item.result_price ?? item.target)}`] as const)
      : item.result === "miss"
        ? (["destructive", "Errou", `fechou o prazo em ${displayMoney(item.result_price ?? item.price)}`] as const)
        : (["secondary", "Em aberto", `prazo até ${displayMonthYear(item.deadline)}`] as const);

  return (
    <span className="inline-flex items-center gap-2">
      <Badge variant={variant} size="tag">
        {label}
      </Badge>
      <span className="text-xs text-muted-foreground">{detail}</span>
    </span>
  );
}

/** O relatório do mês anterior com o desfecho de cada recomendação. */
function PreviousReport({ report }: { report: HouseReport }) {
  return (
    <div className="grid gap-2">
      <h3 className="text-sm font-semibold">Relatório de {displayMonthName(report.month)} · o que acertou</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{capitalize(displayMonthYear(report.month))}</TableHead>
            <TableHead>Recomendação</TableHead>
            <TableHead numeric>Alvo</TableHead>
            <TableHead>Resultado</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.items.map((item) => (
            <TableRow key={item.id}>
              <TableCell>{item.ticker}</TableCell>
              <TableCell>
                <SideBadge side={item.side} />
              </TableCell>
              <TableCell numeric>{displayMoney(item.target)}</TableCell>
              <TableCell>
                <Outcome item={item} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

/** Antes do primeiro relatório: quando ele chega e a renda do mês, só com o fixo enquanto a sala não negociou. */
function BeforeFirstReport({ mechanic }: BrokerBlockProps) {
  const hasCommission = Number(mechanic.commission) > 0;

  return (
    <>
      {/* Aviso do primeiro relatório */}
      <BlockBand>
        <div className="grid gap-1">
          <span className="text-[13px] font-semibold">Ainda sem relatório.</span>
          <p className="text-[13px]">
            O de {displayMonthName(mechanic.next_report_on)} chega em {displayShortDate(mechanic.next_report_on)}, com 3
            a 5 ações. O placar começa quando o prazo da primeira recomendação vencer.
          </p>
        </div>
      </BlockBand>

      {/* Renda do mês */}
      <div className="flex items-center justify-between gap-3 text-[13px]">
        <span className="grid gap-0.5">
          <span className="font-semibold">Renda do mês</span>
          <span className="text-xs text-muted-foreground">
            {hasCommission
              ? `fixo ${displayMoney(mechanic.fixed_income)} + comissão ${displayMoney(mechanic.commission)}`
              : "só o fixo: a sala ainda não negociou nada"}
          </span>
        </span>
        <span className="font-mono font-medium">{displayMoney(mechanic.income)}</span>
      </div>
    </>
  );
}
