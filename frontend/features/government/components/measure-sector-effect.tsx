import { MetricHint } from "@/shared/components/metric-hint";
import type { MeasurePreview } from "@/types";
import { FAVORITISM, SECTOR_BOOST } from "../lib/government-metrics";
import { favoritismSentence, worksBoostSentence } from "../lib/sector-address";

type MeasureSectorEffectProps = {
  address: { sector: string | null; segment: string | null };
  boost: MeasurePreview["sector_boost"];
  favoritism: MeasurePreview["favoritism"];
};

/** O que a obra com endereço faz: a alta das ações do alvo e o que o favorecimento custa em aprovação. */
export function MeasureSectorEffect({ address, boost, favoritism }: MeasureSectorEffectProps) {
  if (!address.sector || boost === null) return null;

  return (
    <ul className="grid divide-y rounded-lg border px-3 text-[13px]">
      <li className="flex items-center gap-1 py-1.5">
        {worksBoostSentence(address, boost)}
        <MetricHint metric={SECTOR_BOOST} />
      </li>
      {favoritism !== null && Number(favoritism) > 0 && (
        <li className="flex items-center gap-1 py-1.5">
          {favoritismSentence(favoritism)}
          <MetricHint metric={FAVORITISM} />
        </li>
      )}
    </ul>
  );
}
