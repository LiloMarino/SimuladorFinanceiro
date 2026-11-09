import { FlagBr } from "@/shared/components/icons/flag-br";
import { FlagUs } from "@/shared/components/icons/flag-us";
import { ASSET_ORIGIN_LABELS } from "@/shared/lib/asset-origin";
import type { AssetOrigin } from "@/types";

type AssetOriginFlagProps = { origin: AssetOrigin; size?: number };

/** A bandeira da origem do ativo: Brasil para o nacional, Estados Unidos para o internacional. */
export function AssetOriginFlag({ origin, size = 16 }: AssetOriginFlagProps) {
  const Flag = origin === "FOREIGN" ? FlagUs : FlagBr;
  return (
    <span role="img" aria-label={ASSET_ORIGIN_LABELS[origin]} className="inline-flex shrink-0">
      <Flag size={size} />
    </span>
  );
}
