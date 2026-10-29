import { TriangleAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { EffectSpark } from "@/shared/components/effect-spark";
import { InfoHint } from "@/shared/components/info-hint";
import { SpendingIcon } from "@/shared/components/spending-icon";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { inflationTone, phaseText, signedIpca, signedStocks } from "@/shared/lib/effects";
import { isSpending } from "@/shared/lib/spending-kinds";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { EconomyEffect, EconomyPanel } from "@/types";
import { effectLabel, inflationBreakdown, stocksEffect, sumEffects } from "../lib/economy";
import { EFFECT_IPCA, EFFECT_SELIC, EFFECT_STOCKS } from "../lib/economy-metrics";

const TONE = { destructive: "text-destructive", success: "text-success", default: "text-muted-foreground" } as const;
const BIG_SHIFT = 2;

/** Um tom de laranja por medida, da mais pesada à mais leve. */
const shade = (index: number) => `color-mix(in srgb, var(--warning) ${Math.max(30, 100 - index * 22)}%, transparent)`;

const stocksTone = (fraction: number) =>
  Math.abs(fraction) < 0.0005 ? TONE.default : fraction < 0 ? TONE.destructive : TONE.success;

type EffectsCardProps = { panel: EconomyPanel; effects: EconomyEffect[] };

/** O que cada medida de gasto aprovada soma hoje à inflação, à SELIC e à bolsa, e de onde vem o IPCA da partida. */
export function EffectsCard({ panel, effects }: EffectsCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-4">
          <div className="flex items-start justify-between gap-4">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Efeitos das medidas de gasto</h2>
              <span className="text-[13px] text-muted-foreground">
                Quanto cada medida aprovada soma hoje à inflação, à SELIC e à bolsa. O efeito chega depois de a medida
                valer, fica cheio por um tempo e cai pela metade a cada 12 meses.
              </span>
            </div>
            <Badge variant="secondary" size="sm">
              a sala vê
            </Badge>
          </div>

          {effects.length === 0 ? <NoEffects /> : <EffectsBody panel={panel} effects={effects} />}
        </div>
      </CardContent>
    </Card>
  );
}

function NoEffects() {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyTitle>Nenhuma medida de gasto mexe na inflação agora</EmptyTitle>
        <EmptyDescription>
          A inflação e a SELIC da partida são as da história. Quando o Congresso aprovar uma medida de gasto, o efeito
          aparece aqui.
        </EmptyDescription>
      </EmptyHeader>
      <Link to="/government" className="text-sm font-medium text-info hover:underline">
        Propor no Governo ›
      </Link>
    </Empty>
  );
}

function EffectsBody({ panel, effects }: { panel: EconomyPanel; effects: EconomyEffect[] }) {
  const today = panel.points.at(-1);
  if (!today) return null;
  const ipcaShift = sumEffects(effects, "inflation");
  const selicShift = sumEffects(effects, "selic");
  const stocksShift = stocksEffect(today);

  return (
    <>
      {ipcaShift >= BIG_SHIFT && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertTitle>As medidas somam {signedIpca(ipcaShift).replace("+", "")} pontos à inflação</AlertTitle>
          <AlertDescription>
            IPCA de {displayPercent(today.ipca, 1)}
            {today.stored_ipca !== null && `, contra ${displayPercent(today.stored_ipca, 1)} na história`}, e a SELIC{" "}
            {signedIpca(selicShift).replace("+", "")} pontos acima. Cortar gasto tira inflação na mesma medida, com
            meses de atraso.
          </AlertDescription>
        </Alert>
      )}

      <IpcaBreakdown today={today} effects={effects} />

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Medida</TableHead>
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
          <TableRow variant="current">
            <TableCell>Todas as medidas juntas</TableCell>
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
        O Banco Central sobe a SELIC 1,5 vez o que as medidas somam à inflação, e cada ponto de SELIC tira 2,9% da bolsa
        no trimestre, mais nas ações de beta alto (as que se mexem mais que o Ibovespa). Cortar gasto faz o caminho
        inverso.
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

type BreakdownProps = { today: EconomyPanel["points"][number]; effects: EconomyEffect[] };

/** O IPCA de hoje em barra: a história e, empilhado, o que cada tipo de medida soma; o que tira fica só na lista. */
function IpcaBreakdown({ today, effects }: BreakdownProps) {
  const parts = inflationBreakdown(effects);
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
              key={part.kind}
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
          <PartLine key={part.kind} part={part} index={adds.indexOf(part)} />
        ))}
        <dt className="border-t pt-1.5 font-semibold">= IPCA da partida</dt>
        <dd className="border-t pt-1.5 text-right font-mono font-semibold">{displayPercent(today.ipca, 2)}</dd>
      </dl>
    </div>
  );
}

type PartLineProps = { part: { kind: EconomyEffect["kind"]; points: number }; index: number };

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
        {part.points > 0 ? "+" : "−"} {effectLabel(part)}
      </dt>
      <dd className={cn("text-right font-mono font-semibold", TONE[inflationTone(part.points)])}>
        {signedIpca(part.points)}
      </dd>
    </>
  );
}
