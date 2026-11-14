import type { CSSProperties } from "react";
import { Badge } from "@/shared/components/ui/badge";
import type { Order } from "@/types";
import { ownerBadge } from "../lib/order-owner";

const VARIANT = { player: "owner-player", fund: "owner-fund", neutral: "owner-neutral" } as const;

/** Selo de quem pôs a ordem: a sigla na cor do jogador, da gestora ou em cinza. */
export function OrderOwnerBadge({ order }: { order: Order }) {
  const { label, tone, color } = ownerBadge(order);
  const style = color
    ? ({ "--owner": color.background, "--owner-foreground": color.foreground } as CSSProperties)
    : undefined;

  return (
    <Badge variant={VARIANT[tone]} size="sm" style={style} aria-hidden="true">
      {label}
    </Badge>
  );
}
