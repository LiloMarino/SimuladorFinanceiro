import type { CSSProperties } from "react";
import { Anchor, Factory, Landmark, PiggyBank, Scale, TrendingUp, type LucideIcon } from "lucide-react";
import type { VoterValue } from "@/types";
import { VALUE_INFO } from "./voters";

export const VALUE_ICONS: Record<VoterValue, LucideIcon> = {
  FREE_MARKET: TrendingUp,
  SOCIAL_JUSTICE: Scale,
  STABILITY: Anchor,
  DEVELOPMENT: Factory,
  SAVER_PROTECTION: PiggyBank,
  PUBLIC_SERVICE: Landmark,
};

/** A cor da bandeira como variável CSS, para o selo e para o emblema. */
export const tintOf = (value: VoterValue) => ({ "--tint": VALUE_INFO[value].color }) as CSSProperties;
