import { displayIsoDate, displayMoney, displayPercent, displaySignedMoney } from "@/shared/lib/utils/display";
import type { NetworthPoint } from "../lib/networth-model";

const WIDTH = 236;

/** Largura do tooltip e folga até o ponteiro: o gráfico decide de que lado abrir. */
export const TOOLTIP_WIDTH = WIDTH;
export const TOOLTIP_GAP = 14;

function Row({ swatch, label, value, tone }: { swatch?: string; label: string; value: string; tone?: "debt" }) {
  return (
    <div className="flex items-center justify-between gap-3 whitespace-nowrap">
      <span className="flex items-center gap-1.5 text-secondary-foreground">
        {swatch && <span className="size-2 rounded-xs" style={{ backgroundColor: swatch }} aria-hidden="true" />}
        {label}
      </span>
      <span className={tone === "debt" ? "font-mono text-destructive" : "font-mono"}>{value}</span>
    </div>
  );
}

/** O dia sob o ponteiro: patrimônio por classe, dívida, aportado, ganho e, na corrida, o que falta para a meta. */
export function NetworthTooltip({ point, left }: { point: NetworthPoint; left: number }) {
  const gain = point.networth - point.provided;
  const gainPct = point.provided === 0 ? 0 : gain / point.provided;
  const positive = gain >= 0;

  return (
    <div
      className="pointer-events-none absolute top-1 z-10 grid gap-1.25 rounded-[10px] border border-border bg-popover p-3 text-xs shadow-lg"
      style={{ left, width: WIDTH }}
    >
      <span className="font-mono text-[11px] text-muted-foreground">{displayIsoDate(point.date)}</span>
      <div className="flex items-center justify-between gap-3 text-[13px] font-semibold whitespace-nowrap">
        <span>Patrimônio</span>
        <span className={point.networth < 0 ? "font-mono text-destructive" : "font-mono"}>
          {displaySignedMoney(point.networth)}
        </span>
      </div>
      <Row swatch="var(--chart-1)" label="Renda variável" value={displayMoney(point.equity)} />
      <Row swatch="var(--chart-2)" label="Renda fixa" value={displayMoney(point.fixed)} />
      <Row swatch="var(--input)" label="Caixa" value={displayMoney(point.cash)} />
      {point.debt > 0 && (
        <Row
          swatch="color-mix(in srgb, var(--destructive) 40%, var(--card))"
          label="Dívida"
          value={displaySignedMoney(-point.debt)}
          tone="debt"
        />
      )}
      <div className="grid gap-1.25 border-t border-border pt-1.5">
        <Row label="Aportado" value={displayMoney(point.provided)} />
      </div>
      <div
        className={`flex items-center justify-between gap-3 font-semibold whitespace-nowrap ${positive ? "text-success" : "text-destructive"}`}
      >
        <span>{positive ? "Ganho" : "Perda"}</span>
        <span className="font-mono">
          {positive ? "+" : "−"}
          {displayMoney(Math.abs(gain))}
        </span>
      </div>
      <span className="-mt-0.5 text-right font-mono text-[11px] text-muted-foreground">
        {positive ? "+" : "−"}
        {displayPercent(Math.abs(gainPct), 1)} sobre o aportado
      </span>
      {point.goal !== undefined && (
        <Row label="Falta para a meta" value={displayMoney(Math.max(0, point.goal - point.networth))} />
      )}
    </div>
  );
}
