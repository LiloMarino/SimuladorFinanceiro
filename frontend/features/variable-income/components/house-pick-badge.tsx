import { Badge } from "@/shared/components/ui/badge";
import type { HousePick } from "@/types";

const SIDE_LABELS: Record<HousePick["side"], string> = {
  buy: "Casa: compra",
  sell: "Casa: venda",
};

/** O selo da ação que está no relatório da casa do Corretor, com o lado da recomendação. */
export function HousePickBadge({ side, size = "sm" }: { side: HousePick["side"]; size?: "default" | "sm" }) {
  return (
    <Badge variant="profession" size={size}>
      {SIDE_LABELS[side]}
    </Badge>
  );
}
