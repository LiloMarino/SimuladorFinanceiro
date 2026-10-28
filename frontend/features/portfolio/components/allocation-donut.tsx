import { useState } from "react";
import { Link } from "react-router-dom";
import { PieChart as PieChartIcon } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia } from "@/shared/components/ui/empty";
import { displayMoneyCompact, displayMoneyWhole, displayPercent, displaySignedMoney } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";
import {
  assetCount,
  classSlices,
  ringArc,
  sliceAngles,
  topAssets,
  type AssetRow,
  type ClassKey,
  type ClassSlice,
} from "../lib/allocation-model";

const SIZE = 176;
const CENTER = SIZE / 2;
const OUTER = 86;
const INNER = 63.64;
// A fatia sob o ponteiro cresce para fora do anel
const GROWTH = 4;

/** Onde está o patrimônio: um anel por classe (caixa incluído) e, ao lado, as classes e os maiores ativos. */
export function AllocationDonut({ portfolio }: { portfolio: PortfolioState }) {
  const [hovered, setHovered] = useState<ClassKey | null>(null);
  const slices = classSlices(portfolio);
  const assets = topAssets(portfolio);
  const debt = Number(portfolio.debt);
  const onlyCash = assets.length === 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1.5">
            Distribuição do patrimônio
            <InfoHint label="Como ler a distribuição">
              <div className="grid gap-1 text-left text-xs leading-snug">
                <span>O anel divide o que você tem hoje (caixa, renda fixa e ações), sem descontar a dívida.</span>
                <span>Ex.: R$ 50.000 em ações, de R$ 200.000 que você tem, são 25%.</span>
              </div>
            </InfoHint>
          </span>
        </CardTitle>
        <CardDescription>O que você tem hoje, por classe e os maiores ativos</CardDescription>
      </CardHeader>
      <CardContent>
        {slices.length === 0 ? (
          <Empty variant="dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <PieChartIcon />
              </EmptyMedia>
              <EmptyDescription>
                Seus investimentos aparecem aqui, separados entre renda variável, renda fixa e caixa.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <div
            className={`grid items-start gap-6 lg:gap-9 ${onlyCash ? "lg:grid-cols-[176px_minmax(0,24rem)]" : "lg:grid-cols-[176px_300px_minmax(0,1fr)]"}`}
          >
            <Ring portfolio={portfolio} slices={slices} hovered={hovered} onHover={setHovered} />

            <div className="grid content-start gap-1.5">
              <span className="pb-0.5 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                Por classe
              </span>
              {slices.map((slice) => (
                <ClassRow key={slice.key} slice={slice} active={hovered === slice.key} onHover={setHovered} />
              ))}

              {onlyCash && (
                <div className="mt-2 grid gap-2.5">
                  <span className="text-[13px] text-muted-foreground">
                    Dinheiro parado não rende. Compre um título na Renda fixa ou uma ação na Renda variável.
                  </span>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/fixed-income" />}>
                      Renda fixa
                    </Button>
                    <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/variable-income" />}>
                      Renda variável
                    </Button>
                  </div>
                </div>
              )}

              {debt > 0 && (
                <div className="mt-1.5 grid gap-1 border-t border-border pt-2.5 text-[13px]">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Dívida</span>
                    <span className="text-destructive tabular-nums">{displaySignedMoney(-debt)}</span>
                  </div>
                  <div className="flex justify-between font-semibold">
                    <span>Patrimônio</span>
                    <span className={`tabular-nums ${Number(portfolio.total_networth) < 0 ? "text-destructive" : ""}`}>
                      {displaySignedMoney(portfolio.total_networth)}
                    </span>
                  </div>
                  <span className="text-[11px] text-muted-foreground">O que você tem menos o que deve</span>
                </div>
              )}
            </div>

            {!onlyCash && <AssetList assets={assets} />}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Ring({
  portfolio,
  slices,
  hovered,
  onHover,
}: {
  portfolio: PortfolioState;
  slices: ClassSlice[];
  hovered: ClassKey | null;
  onHover: (key: ClassKey | null) => void;
}) {
  const angles = sliceAngles(slices.map((s) => s.fraction));
  const count = assetCount(portfolio);
  const holdsCash = Number(portfolio.cash) > 0;
  const caption =
    count === 0 ? "tudo em caixa" : `${count} ${count === 1 ? "ativo" : "ativos"}${holdsCash ? " + caixa" : ""}`;

  return (
    <div className="relative" style={{ width: SIZE, height: SIZE }}>
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} className="overflow-visible" aria-hidden="true">
        {slices.map((slice, i) => {
          const angle = angles[i];
          if (!angle) return null;
          const grown = hovered === slice.key;
          return (
            <path
              key={slice.key}
              d={ringArc(CENTER, CENTER, grown ? OUTER + GROWTH : OUTER, INNER, angle.start, angle.end)}
              fillRule="evenodd"
              style={{ fill: slice.color }}
              onPointerEnter={() => onHover(slice.key)}
              onPointerLeave={() => onHover(null)}
            />
          );
        })}
      </svg>
      <div className="pointer-events-none absolute inset-0 grid place-content-center text-center">
        <span className="text-[11px] text-muted-foreground">Você tem</span>
        <span className="text-[15px] font-semibold tabular-nums">{displayMoneyCompact(portfolio.assets_value)}</span>
        <span className="text-[11px] text-muted-foreground">{caption}</span>
      </div>
    </div>
  );
}

function ClassRow({
  slice,
  active,
  onHover,
}: {
  slice: ClassSlice;
  active: boolean;
  onHover: (key: ClassKey | null) => void;
}) {
  return (
    <div
      className={`-mx-1.5 flex min-w-0 items-center gap-2 rounded-md px-1.5 py-0.5 text-[13px] font-semibold ${active ? "bg-subtle" : ""}`}
      onPointerEnter={() => onHover(slice.key)}
      onPointerLeave={() => onHover(null)}
    >
      <span className="size-2.25 shrink-0 rounded-xs" style={{ backgroundColor: slice.color }} aria-hidden="true" />
      <span className="min-w-0 flex-1 truncate">
        {slice.label}
        {slice.key === "cash" && <span className="text-xs font-normal text-muted-foreground"> · não rende</span>}
      </span>
      <span className="text-xs font-medium tabular-nums">{displayMoneyWhole(slice.value)}</span>
      <span className="w-11.5 text-right tabular-nums">{displayPercent(slice.fraction, 1)}</span>
    </div>
  );
}

function AssetList({ assets }: { assets: AssetRow[] }) {
  return (
    <div className="grid min-w-0 content-start gap-1">
      <div className="flex justify-between pb-0.5">
        <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
          Maiores ativos
        </span>
        <span className="text-[11px] text-muted-foreground">% do que você tem</span>
      </div>
      <ul
        className="grid grid-flow-col grid-cols-2 gap-x-10 gap-y-1"
        style={{ gridTemplateRows: `repeat(${Math.ceil(assets.length / 2)}, auto)` }}
      >
        {assets.map((asset, i) => (
          <li key={`${asset.name}-${i}`} className="-mx-1.5 flex min-w-0 items-center gap-2 px-1.5 py-0.5 text-[13px]">
            <span
              className="size-2.25 shrink-0 rounded-xs"
              style={{ backgroundColor: asset.color }}
              aria-hidden="true"
            />
            <span
              className="min-w-0 flex-1 truncate"
              title={asset.count === undefined ? asset.name : `Outros · ${asset.count} ativos`}
            >
              {asset.name}
              {asset.count !== undefined && (
                <span className="text-xs text-muted-foreground"> · {asset.count} ativos</span>
              )}
            </span>
            <span className="w-11.5 text-right tabular-nums">{displayPercent(asset.fraction, 1)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
