import { useState } from "react";
import { Info } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayPercent,
  displayShortDate,
  displaySignedMoney,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { ReturnsPlayer } from "@/types";
import { RETURN_SOURCES } from "../../lib/metrics";
import { buildWaterfall, shareOfReturn, type Waterfall } from "../../lib/return-sources";
import { PlayerName } from "./player-name";
import { ChartCard } from "./shared";

type Unit = "MONEY" | "PERCENT";

interface ReturnSourcesCardProps {
  /** Quem a cascata mostra, cada um com o nome que aparece no rótulo. */
  subjects: { player: ReturnsPlayer; label: string; isYou: boolean }[];
}

/** Cascata do retorno da partida: de onde veio cada parte do resultado, em reais ou em % do aporte. */
export function ReturnSourcesCard({ subjects }: ReturnSourcesCardProps) {
  const [unit, setUnit] = useState<Unit>("MONEY");

  return (
    <ChartCard
      metric={RETURN_SOURCES}
      action={
        <ToggleGroup
          variant="segmented"
          aria-label="Unidade das parcelas"
          value={[unit]}
          onValueChange={(values) => values[0] && setUnit(values[0] as Unit)}
        >
          <ToggleGroupItem value="MONEY">R$</ToggleGroupItem>
          <ToggleGroupItem value="PERCENT">% do aporte</ToggleGroupItem>
        </ToggleGroup>
      }
    >
      <div className="grid gap-6">
        {subjects.map(({ player, label, isYou }) => (
          <SourcesOfPlayer
            key={`${player.simulation_id}|${player.player_nickname}`}
            player={player}
            label={label}
            isYou={isYou}
            unit={unit}
          />
        ))}
      </div>
    </ChartCard>
  );
}

const ROW_GRID = "grid grid-cols-[minmax(0,260px)_minmax(0,1fr)_110px_48px] items-center gap-4";

function SourcesOfPlayer({
  player,
  label,
  isYou,
  unit,
}: {
  player: ReturnsPlayer;
  label: string;
  isYou: boolean;
  unit: Unit;
}) {
  const waterfall = buildWaterfall(player.return_sources);
  const capital = Number(player.capital_provided);
  const since = player.networth[0]?.date;
  const dividends = Number(player.return_sources.dividends);
  const dividendShare = shareOfReturn(dividends, waterfall.total);

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-baseline gap-x-3 text-xs text-muted-foreground">
        <span className="font-medium">
          <PlayerName label={label} isYou={isYou} />
          {since && ` · desde ${displayShortDate(since)}`}
        </span>
        <span>Aporte: {displayMoney(capital)}</span>
      </div>

      <div>
        {waterfall.rows.map((row) => (
          <div key={row.key} className={cn(ROW_GRID, "border-b border-muted py-2.5")}>
            <div className="grid">
              <span className="flex items-center gap-2 text-[13px] font-medium">
                <span className={cn("size-2.5 shrink-0 rounded-[3px]", row.bar)} aria-hidden="true" />
                {row.label}
              </span>
              <span className="pl-[18px] text-xs text-faint-foreground">{row.note}</span>
            </div>
            <WaterfallBar waterfall={waterfall} from={row.start} to={row.end} className={row.bar} />
            <b className={cn("text-right font-mono text-[13px]", row.value < 0 && "text-destructive")}>
              {displayAmount(row.value, capital, unit)}
            </b>
            <span className="text-right font-mono text-xs text-faint-foreground">
              {displayShare(shareOfReturn(row.value, waterfall.total))}
            </span>
          </div>
        ))}

        <div className={cn(ROW_GRID, "pt-3")}>
          <b className="pl-[18px] text-sm">Retorno da partida</b>
          <WaterfallBar waterfall={waterfall} from={0} to={waterfall.total} className="bg-primary" tall />
          <b className="text-right font-mono text-[15px]">{displayAmount(waterfall.total, capital, unit)}</b>
          <span className="text-right font-mono text-xs text-faint-foreground">
            {unit === "MONEY" && capital > 0 ? displayPercent(waterfall.total / capital, 1) : "100%"}
          </span>
        </div>
      </div>

      {dividends > 0 && dividendShare !== null && (
        <Alert variant="info">
          <Info />
          <AlertDescription>
            Proventos foram <b>{displayPercent(dividendShare, 0)}</b> do resultado: <b>{displayMoney(dividends)}</b> que
            caíram no caixa sem você vender nada.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

/** Uma barra da cascata, de `from` a `to` na escala do acumulado, com a linha do zero atrás. */
function WaterfallBar({
  waterfall,
  from,
  to,
  className,
  tall = false,
}: {
  waterfall: Waterfall;
  from: number;
  to: number;
  className: string;
  tall?: boolean;
}) {
  const span = waterfall.max - waterfall.min || 1;
  const left = ((Math.min(from, to) - waterfall.min) / span) * 100;
  const width = (Math.abs(to - from) / span) * 100;
  const zero = ((0 - waterfall.min) / span) * 100;

  return (
    <div className={cn("relative", tall ? "h-[26px]" : "h-[22px]")} aria-hidden="true">
      <i className="absolute inset-y-0 w-px bg-input" style={{ left: `${zero}%` }} />
      <i
        className={cn("absolute inset-y-[3px] rounded", className)}
        style={{ left: `${left}%`, width: `max(${width}%, 2px)` }}
      />
    </div>
  );
}

/** Reais com sinal, ou a parcela como fração do aporte. */
function displayAmount(value: number, capital: number, unit: Unit) {
  if (unit === "PERCENT") return capital > 0 ? displaySignedPercent(value / capital, 1) : "—";
  return value > 0 ? `+${displayMoney(value)}` : displaySignedMoney(value);
}

/** A fatia da parcela no retorno, sem casas decimais. */
function displayShare(share: number | null) {
  return share === null ? "—" : displayPercent(share, 0);
}
