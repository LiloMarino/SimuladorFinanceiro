import { HandCoins, HardHat, Landmark, PiggyBank } from "lucide-react";
import type { ComponentType } from "react";
import type { SpendingKind } from "@/shared/lib/spending-kinds";

const ICONS: Record<SpendingKind, ComponentType<{ className?: string | undefined }>> = {
  WELFARE_SPENDING: HandCoins,
  SERVANT_RAISE: Landmark,
  RETIREE_RAISE: PiggyBank,
  PUBLIC_WORKS: HardHat,
};

/** O ícone de cada medida de gasto público. */
export function SpendingIcon({ kind, className }: { kind: SpendingKind; className?: string | undefined }) {
  const Icon = ICONS[kind];
  return <Icon className={className} />;
}
