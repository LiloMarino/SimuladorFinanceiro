import {
  CloudLightning,
  CircleHelp,
  Crown,
  Egg,
  Flag,
  Flame,
  Gem,
  Hammer,
  HandCoins,
  Hourglass,
  Landmark,
  Lock,
  type LucideIcon,
  Percent,
  PiggyBank,
  Rocket,
  ShieldCheck,
  ShoppingCart,
  Snowflake,
  Sunrise,
  Target,
  TrendingUp,
  Trophy,
  Users,
  Wallet,
} from "lucide-react";
import { cn } from "@/shared/lib/utils";
import type { AchievementIconName } from "@/types";

// Cada valor do enum da API tem o seu ícone: o tsc acusa quando a API ganha um novo
const ICONS: Record<AchievementIconName, LucideIcon> = {
  SHOPPING_CART: ShoppingCart,
  LANDMARK: Landmark,
  HAND_COINS: HandCoins,
  HAMMER: Hammer,
  TRENDING_UP: TrendingUp,
  PIGGY_BANK: PiggyBank,
  GEM: Gem,
  CROWN: Crown,
  EGG: Egg,
  CLOUD_LIGHTNING: CloudLightning,
  SNOWFLAKE: Snowflake,
  PERCENT: Percent,
  TARGET: Target,
  SHIELD_CHECK: ShieldCheck,
  TROPHY: Trophy,
  USERS: Users,
  FLAG: Flag,
  ROCKET: Rocket,
  HOURGLASS: Hourglass,
  SUNRISE: Sunrise,
  WALLET: Wallet,
  FLAME: Flame,
};

type AchievementIconProps = {
  name: AchievementIconName;
  /** Bloqueada fica cinza com um cadeado; a secreta bloqueada vira uma interrogação de borda tracejada */
  state: "unlocked" | "locked" | "secret";
  size?: "sm" | "md" | "lg";
  /** Sobre o fundo escuro do aviso, onde o selo escuro de sempre sumiria */
  onDark?: boolean;
};

/** O selo da conquista: ícone dourado sobre fundo escuro quando desbloqueada. */
export function AchievementIcon({ name, state, size = "md", onDark = false }: AchievementIconProps) {
  const Icon = state === "secret" ? CircleHelp : ICONS[name];
  const unlocked = state === "unlocked";

  return (
    <span
      aria-hidden="true"
      className={cn(
        "relative inline-flex shrink-0 items-center justify-center",
        size === "sm" && "size-9 rounded-[9px] [&>svg]:size-[18px]",
        size === "md" && "size-10 rounded-[10px] [&>svg]:size-5",
        size === "lg" && "size-13 rounded-[14px] [&>svg]:size-[26px]",
        unlocked &&
          (onDark
            ? "bg-sidebar-accent text-toast-warning ring-1 ring-white/10 ring-inset"
            : "bg-sidebar text-toast-warning ring-1 ring-sidebar-accent ring-inset"),
        state === "locked" && "bg-muted text-toast-muted",
        state === "secret" && "border-[1.5px] border-dashed border-input bg-subtle text-toast-muted",
      )}
    >
      <Icon />
      {state === "locked" && (
        <span className="absolute -right-[5px] -bottom-[5px] inline-flex size-5 items-center justify-center rounded-full border border-border bg-card text-faint-foreground [&>svg]:size-[11px] [&>svg]:stroke-[2.5]">
          <Lock />
        </span>
      )}
    </span>
  );
}
