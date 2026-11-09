import {
  Briefcase,
  Building2,
  CreditCard,
  DollarSign,
  Flame,
  Landmark,
  Percent,
  ShieldAlert,
  ShoppingCart,
  TrendingUp,
  TriangleAlert,
  Users,
  type LucideIcon,
} from "lucide-react";
import { Link } from "react-router-dom";
import { EffectSpark } from "@/shared/components/effect-spark";
import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { SpendingIcon } from "@/shared/components/spending-icon";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { inflationTone, phaseText, signedIpca, signedStocks } from "@/shared/lib/effects";
import { isSpending } from "@/shared/lib/spending-kinds";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { EconomyEffect, EconomyLinkEffect, EconomyPanel } from "@/types";
import {
  activeLinks,
  inflationBreakdown,
  LINK_METRIC,
  selicByGovernment,
  stocksEffect,
  sumEffects,
  type InflationPart,
} from "../lib/economy";
import { EFFECT_IPCA, EFFECT_SELIC, EFFECT_STOCKS, signedPoints } from "../lib/economy-metrics";

const TONE = { destructive: "text-destructive", success: "text-success", default: "text-muted-foreground" } as const;
const BIG_SHIFT = 2;

/** Um tom de laranja por medida, da mais pesada à mais leve. */
const shade = (index: number) => `color-mix(in srgb, var(--warning) ${Math.max(30, 100 - index * 22)}%, transparent)`;

const stocksTone = (fraction: number) =>
  Math.abs(fraction) < 0.0005 ? TONE.default : fraction < 0 ? TONE.destructive : TONE.success;

/** O ícone e o assunto do desvio de cada ligação, para a linha da tabela. */
const LINK_ROW: Record<EconomyLinkEffect["link"], { icon: LucideIcon; subject: string }> = {
  PHILLIPS: { icon: Users, subject: "Desemprego" },
  FISCAL_RISK: { icon: ShieldAlert, subject: "Prêmio de risco" },
  DOLLAR: { icon: DollarSign, subject: "Dólar" },
  GDP: { icon: TrendingUp, subject: "PIB" },
  REAL_RATE: { icon: Percent, subject: "Juro real" },
  SELIC: { icon: Landmark, subject: "SELIC" },
  INFLATION_BRAKE: { icon: Flame, subject: "IPCA acima de 12%" },
  CROWDING_OUT: { icon: CreditCard, subject: "Prêmio de risco" },
  CONSUMPTION_TAX: { icon: ShoppingCart, subject: "Alíquota do consumo" },
  CORPORATE_TAX: { icon: Building2, subject: "Alíquota do IR das empresas" },
  PAYROLL_TAX: { icon: Briefcase, subject: "Alíquota da folha" },
};

type EffectsCardProps = { panel: EconomyPanel; effects: EconomyEffect[]; links: EconomyLinkEffect[] };

/** O que cada medida de gasto aprovada e cada ligação da economia somam hoje à inflação, à SELIC e à bolsa. */
export function EffectsCard({ panel, effects, links }: EffectsCardProps) {
  const active = activeLinks(links);

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-4">
          <div className="grid gap-1">
            <h2 className="text-[15px] font-semibold">Efeitos do governo na economia</h2>
            <span className="text-[13px] text-muted-foreground">
              Quanto cada medida aprovada e cada ligação da economia somam hoje à inflação, à SELIC e à bolsa. O efeito
              da medida chega depois de ela valer, fica cheio por um tempo e cai pela metade a cada 12 meses; o da
              ligação segue o quanto a partida se afastou da história no último mês fechado.
            </span>
          </div>

          {effects.length === 0 && active.length === 0 ? (
            <NoEffects />
          ) : (
            <EffectsBody panel={panel} effects={effects} links={active} byGovernment={selicByGovernment(links)} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function NoEffects() {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyTitle>Nada do governo mexe na economia agora</EmptyTitle>
        <EmptyDescription>
          A inflação, a SELIC e a bolsa da partida são as da história. Quando o Congresso aprovar uma medida de gasto,
          ou a dívida e o desemprego se afastarem da história, o efeito aparece aqui.
        </EmptyDescription>
      </EmptyHeader>
      <Link to="/government" className="text-sm font-medium text-info hover:underline">
        Propor no Governo ›
      </Link>
    </Empty>
  );
}

type EffectsBodyProps = {
  panel: EconomyPanel;
  effects: EconomyEffect[];
  links: EconomyLinkEffect[];
  byGovernment: boolean;
};

function EffectsBody({ panel, effects, links, byGovernment }: EffectsBodyProps) {
  const today = panel.points.at(-1);
  if (!today) return null;
  const ipcaShift = sumEffects(effects, "inflation") + sumEffects(links, "inflation");
  const selicShift = sumEffects(effects, "selic") + sumEffects(links, "selic");
  const stocksShift = stocksEffect(today);

  return (
    <>
      {ipcaShift >= BIG_SHIFT && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertTitle>O governo soma {signedIpca(ipcaShift).replace("+", "")} pontos à inflação</AlertTitle>
          <AlertDescription>
            IPCA de {displayPercent(today.ipca, 1)}
            {today.stored_ipca !== null && `, contra ${displayPercent(today.stored_ipca, 1)} na história`}, e a SELIC{" "}
            {signedIpca(selicShift).replace("+", "")} pontos acima. Cortar gasto tira inflação na mesma medida, com
            meses de atraso.
          </AlertDescription>
        </Alert>
      )}

      <IpcaBreakdown today={today} parts={inflationBreakdown(effects, links)} />

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Medida ou ligação</TableHead>
            <TableHead>Onde o efeito está</TableHead>
            <TableHead numeric>
              <HeadHint label="IPCA" info={EFFECT_IPCA} />
            </TableHead>
            <TableHead numeric>
              <HeadHint label="SELIC" info={EFFECT_SELIC} />
            </TableHead>
            <TableHead numeric>
              <HeadHint label="Bolsa no trimestre" info={EFFECT_STOCKS} />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {effects.map((effect) => (
            <EffectRow key={effect.measure_id} effect={effect} />
          ))}
          {links.map((link) => (
            <LinkRow key={link.link} link={link} />
          ))}
          <TableRow variant="current">
            <TableCell>Tudo junto</TableCell>
            <TableCell />
            <TableCell numeric className={TONE[inflationTone(ipcaShift)]}>
              {signedIpca(ipcaShift)}
            </TableCell>
            <TableCell numeric className={TONE[inflationTone(selicShift)]}>
              {signedIpca(selicShift)}
            </TableCell>
            <TableCell numeric className={stocksShift === null ? "" : stocksTone(stocksShift)}>
              {stocksShift === null ? "—" : signedStocks(stocksShift)}
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>

      <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
        {byGovernment
          ? "A SELIC é a que o presidente fixou no Copom: o Banco Central não reage ao que as medidas e as ligações somam à inflação."
          : "O Banco Central sobe a SELIC 1,5 vez o que as medidas e as ligações somam à inflação."}{" "}
        Cada ponto de SELIC ou de prêmio de risco tira 2,9% da bolsa no trimestre, mais nas ações de beta alto (as que
        se mexem mais que o Ibovespa); o PIB acima da história a levanta. A inflação acima de 12% e o prêmio de risco
        acima da história tiram crescimento do PIB, e o PIB menor sobe a dívida. A ligação de um mês vale a partir do
        seguinte. Cortar gasto faz o caminho inverso.
      </p>
    </>
  );
}

type HeadHintProps = { label: string; info: { definition: string; example: string; reading: string } };

function HeadHint({ label, info }: HeadHintProps) {
  return (
    <span className="inline-flex items-center gap-1">
      {label}
      <InfoHint label={`O que é ${label}`}>
        <div className="space-y-1 text-left">
          <p>{info.definition}</p>
          <p>{info.example}</p>
          <p>{info.reading}</p>
        </div>
      </InfoHint>
    </span>
  );
}

function EffectRow({ effect }: { effect: EconomyEffect }) {
  return (
    <TableRow>
      <TableCell className="max-w-90 whitespace-normal">
        <span className="flex items-center gap-3">
          {isSpending(effect.kind) && (
            <span className="grid size-7 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground">
              <SpendingIcon kind={effect.kind} className="size-4" />
            </span>
          )}
          <span className="grid min-w-0 gap-0.5">
            <span className="font-medium [overflow-wrap:anywhere]">{effect.title}</span>
            <span className="text-xs text-muted-foreground">vale desde {displayDayMonth(effect.effective)}</span>
          </span>
        </span>
      </TableCell>
      <TableCell>
        <span className="flex items-center gap-2.5">
          <EffectSpark curve={effect.curve} elapsedMonths={effect.elapsed_months} width={110} height={30} />
          <span className="max-w-50 text-[12.5px] whitespace-normal text-muted-foreground">
            {phaseText(effect.phase, effect.peak_on, effect.faded_on)}
          </span>
        </span>
      </TableCell>
      <TableCell numeric className={TONE[inflationTone(effect.inflation)]}>
        {signedIpca(effect.inflation)}
      </TableCell>
      <TableCell numeric className={TONE[inflationTone(effect.selic)]}>
        {signedIpca(effect.selic)}
      </TableCell>
      <TableCell numeric className={stocksTone(Number(effect.stocks))}>
        {signedStocks(effect.stocks)}
      </TableCell>
    </TableRow>
  );
}

function LinkRow({ link }: { link: EconomyLinkEffect }) {
  const metric = LINK_METRIC[link.link];
  const { icon: Icon, subject } = LINK_ROW[link.link];
  return (
    <TableRow>
      <TableCell className="max-w-90 whitespace-normal">
        <span className="flex items-center gap-3">
          <span className="grid size-7 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground">
            <Icon className="size-4" />
          </span>
          <span className="grid min-w-0 gap-0.5">
            <span className="inline-flex items-center gap-1 font-medium">
              {metric.label}
              <MetricHint metric={metric} />
            </span>
            <span className="text-xs text-muted-foreground">{metric.description}</span>
          </span>
        </span>
      </TableCell>
      <TableCell>
        <span className="grid text-[12.5px] whitespace-normal text-muted-foreground">
          <span>
            {subject} {metric.format(link.gap)} contra a história
          </span>
          {Math.abs(Number(link.growth)) >= 0.0005 && (
            <span>Soma {signedPoints(Number(link.growth))} ao crescimento do PIB</span>
          )}
          {Math.abs(Number(link.unemployment)) >= 0.0001 && (
            <span>Soma {signedPoints(Number(link.unemployment))} ao desemprego por ano</span>
          )}
        </span>
      </TableCell>
      <TableCell numeric className={TONE[inflationTone(link.inflation)]}>
        {signedIpca(link.inflation)}
      </TableCell>
      <TableCell numeric className={TONE[inflationTone(link.selic)]}>
        {signedIpca(link.selic)}
      </TableCell>
      <TableCell numeric className={stocksTone(Number(link.stocks))}>
        {signedStocks(link.stocks)}
      </TableCell>
    </TableRow>
  );
}

type BreakdownProps = { today: EconomyPanel["points"][number]; parts: InflationPart[] };

/** O IPCA de hoje em barra: a história e, empilhado, o que cada medida e ligação soma; o que tira fica só na lista. */
function IpcaBreakdown({ today, parts }: BreakdownProps) {
  const history = (today.stored_ipca === null ? Number(today.ipca) : Number(today.stored_ipca)) * 100;
  const adds = parts.filter((part) => part.points > 0);
  const cuts = parts.filter((part) => part.points < 0);
  const total = history + adds.reduce((sum, part) => sum + part.points, 0) || 1;
  const cut = cuts.reduce((sum, part) => sum + part.points, 0);

  return (
    <div className="grid items-center gap-x-7 gap-y-4 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div className="grid gap-2">
        <span className="text-sm font-medium">De onde vem o IPCA de {displayPercent(today.ipca, 1)}</span>
        <div
          className="flex h-8.5 overflow-hidden rounded-md bg-muted"
          role="img"
          aria-label="Composição do IPCA de hoje"
        >
          <span
            className="flex items-center justify-center overflow-hidden bg-border text-xs font-semibold whitespace-nowrap"
            style={{ width: `${(history / total) * 100}%` }}
          >
            Na história
          </span>
          {adds.map((part, index) => (
            <span
              key={part.key}
              className="flex items-center justify-center overflow-hidden text-xs font-semibold whitespace-nowrap"
              style={{ width: `${(part.points / total) * 100}%`, background: shade(index) }}
            >
              {part.label}
            </span>
          ))}
        </div>
        <div className="flex justify-between gap-3 text-xs text-muted-foreground">
          <span>0%</span>
          {cuts.length > 0 && (
            <span className="text-center">
              {cuts.map((part) => part.label).join(" e ")} {cuts.length > 1 ? "tiram" : "tira"}{" "}
              {signedIpca(cut).replace("−", "")} ponto{Math.abs(cut) > 1 ? "s" : ""}, por isso não aparece na barra
            </span>
          )}
          <span>{displayPercent(total / 100, 1)}</span>
        </div>
      </div>

      <dl className="grid grid-cols-[minmax(0,1fr)_auto] gap-x-3 gap-y-1 text-[12.5px]">
        <dt className="text-muted-foreground">
          <i className="mr-1.5 inline-block size-2.5 rounded-xs bg-border align-middle" />
          IPCA da história
        </dt>
        <dd className="text-right font-mono font-semibold">{displayPercent(history / 100, 2)}</dd>
        {parts.map((part) => (
          <PartLine key={part.key} part={part} index={adds.indexOf(part)} />
        ))}
        <dt className="border-t pt-1.5 font-semibold">= IPCA da partida</dt>
        <dd className="border-t pt-1.5 text-right font-mono font-semibold">{displayPercent(today.ipca, 2)}</dd>
      </dl>
    </div>
  );
}

type PartLineProps = { part: InflationPart; index: number };

/** Uma linha da lista: a cor da barra para o que soma e um quadrado vazado verde para o que tira. */
function PartLine({ part, index }: PartLineProps) {
  return (
    <>
      <dt className="text-muted-foreground">
        <i
          className={cn(
            "mr-1.5 inline-block size-2.5 rounded-xs align-middle",
            index < 0 && "ring-[1.5px] ring-success ring-inset",
          )}
          style={index >= 0 ? { background: shade(index) } : undefined}
        />
        {part.points > 0 ? "+" : "−"} {part.label}
      </dt>
      <dd className={cn("text-right font-mono font-semibold", TONE[inflationTone(part.points)])}>
        {signedIpca(part.points)}
      </dd>
    </>
  );
}
