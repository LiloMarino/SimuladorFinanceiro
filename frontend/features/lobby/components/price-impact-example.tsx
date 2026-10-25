import { normalizeNumberString } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import { usePriceImpactPreview } from "../hooks/queries/usePriceImpactPreview";

const WIDTH = 190;
const HEIGHT = 88;
const PAD = 8;
// Segunda marca do eixo: o décimo pregão
const MIDDLE_DAY = 10;

type PriceImpactExampleProps = {
  k: string;
  decayDays: string;
  /** Ativo citado no texto; sem ele, o exemplo fala de "uma ação" */
  ticker: string | undefined;
};

/** Exemplo concreto do impacto: quanto uma compra move o preço e a curva até voltar ao histórico. */
export function PriceImpactExample({ k, decayDays, ticker }: PriceImpactExampleProps) {
  const kValue = Number(normalizeNumberString(k));
  const tValue = Number(decayDays);
  const valid = Number.isFinite(kValue) && kValue >= 0 && Number.isInteger(tValue) && tValue >= 1;

  const { data: preview } = usePriceImpactPreview(kValue, tValue, { enabled: valid });

  if (!preview) return null;

  const peak = preview.first_day_impact || 1;
  const lastDay = preview.curve.at(-1)?.day ?? 1;
  const baseline = HEIGHT - PAD;
  const xOf = (day: number) => PAD + ((day - 1) / Math.max(lastDay - 1, 1)) * (WIDTH - 2 * PAD);
  const coords = preview.curve.map((p) => ({
    x: xOf(p.day),
    y: baseline - (p.impact / peak) * (HEIGHT - 2 * PAD - 12),
  }));
  const line = coords.map((c) => `${c.x.toFixed(1)},${c.y.toFixed(1)}`).join(" ");
  const first = coords[0];
  const last = coords.at(-1);
  const area = first && last ? `M${first.x},${baseline} L${line.replaceAll(" ", " L")} L${last.x},${baseline} Z` : "";

  return (
    <div className="grid grid-cols-[1fr_190px] items-center gap-4 rounded-[10px] bg-subtle p-3.5">
      <div className="grid gap-1.5">
        <p className="text-[13px] text-muted-foreground">
          Comprar <b className="text-foreground">{displayPercent(preview.volume_share, 0)} do volume diário</b> de{" "}
          {ticker ?? "uma ação"} sobe o preço{" "}
          <b className="font-mono text-foreground">+{displayPercent(preview.first_day_impact)}</b> no pregão seguinte.
        </p>
        <p className="text-xs text-muted-foreground">O efeito some em {tValue} pregões. Personalizado libera k e T.</p>
      </div>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="h-[88px] w-[190px]"
        role="img"
        aria-label="Curva do impacto até voltar ao histórico"
      >
        <line x1={PAD} y1={baseline} x2={WIDTH - PAD} y2={baseline} stroke="var(--border)" />
        <path d={area} fill="var(--primary)" fillOpacity={0.08} />
        <polyline points={line} fill="none" stroke="var(--primary)" strokeWidth="2" />
        {first && (
          <text x={first.x} y={first.y - 6} className="fill-foreground font-mono text-[10px] font-semibold">
            +{displayPercent(preview.first_day_impact)}
          </text>
        )}
        <text x={PAD} y={HEIGHT - 1} className="fill-faint-foreground font-mono text-[10px]">
          1
        </text>
        {lastDay > MIDDLE_DAY && (
          <text
            x={xOf(MIDDLE_DAY)}
            y={HEIGHT - 1}
            textAnchor="middle"
            className="fill-faint-foreground font-mono text-[10px]"
          >
            {MIDDLE_DAY}
          </text>
        )}
        <text x={WIDTH - PAD} y={HEIGHT - 1} textAnchor="end" className="fill-faint-foreground font-mono text-[10px]">
          {tValue} pregões
        </text>
      </svg>
    </div>
  );
}
