import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import type { PriceImpactPreview } from "@/types";

const WIDTH = 190;
const HEIGHT = 88;
const PAD = 8;

/** Exemplo concreto do impacto: quanto uma compra move o preço e a curva até voltar ao histórico. */
export function PriceImpactExample({ k, decayDays }: { k: string; decayDays: string }) {
  const kValue = Number(normalizeNumberString(k));
  const tValue = Number(decayDays);
  const valid = Number.isFinite(kValue) && kValue >= 0 && Number.isInteger(tValue) && tValue >= 1;

  const { data: preview } = useQuery({
    queryKey: queryKeys.priceImpactPreview(kValue, tValue),
    queryFn: ({ signal }) =>
      apiFetch<PriceImpactPreview>(`/api/simulation/price-impact-preview?k=${kValue}&decay_days=${tValue}`, { signal }),
    enabled: valid,
  });

  if (!preview) return null;

  const peak = preview.first_day_impact || 1;
  const lastDay = preview.curve.at(-1)?.day ?? 1;
  const points = preview.curve
    .map((p) => {
      const x = PAD + ((p.day - 1) / Math.max(lastDay - 1, 1)) * (WIDTH - 2 * PAD);
      const y = HEIGHT - PAD - (p.impact / peak) * (HEIGHT - 2 * PAD - 12);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="flex items-center gap-4 rounded-[10px] bg-subtle p-3.5">
      <p className="flex-1 text-[13px] text-muted-foreground">
        Comprar {displayPercent(preview.volume_share, 0)} do volume diário de uma ação sobe o preço{" "}
        <b className="font-mono text-foreground">+{displayPercent(preview.first_day_impact)}</b> no pregão seguinte. O
        efeito some em {tValue} pregões.
      </p>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="h-[88px] w-[190px] shrink-0"
        role="img"
        aria-label="Curva do impacto até voltar ao histórico"
      >
        <line x1={PAD} y1={HEIGHT - PAD} x2={WIDTH - PAD} y2={HEIGHT - PAD} stroke="var(--border)" />
        <polyline points={points} fill="none" stroke="var(--primary)" strokeWidth="2" />
        <text x={PAD} y={HEIGHT - 1} className="fill-faint-foreground font-mono text-[9px]">
          1
        </text>
        <text x={WIDTH - PAD} y={HEIGHT - 1} textAnchor="end" className="fill-faint-foreground font-mono text-[9px]">
          {tValue} pregões
        </text>
      </svg>
    </div>
  );
}
