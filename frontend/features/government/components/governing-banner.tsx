import { Lock } from "lucide-react";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { displayShortDate } from "@/shared/lib/utils/display";

/** Faixa sob a topbar enquanto o jogador governa: a carteira congelada e até quando. */
export function GoverningBanner() {
  const { data: panel } = useGovernment();
  if (!panel?.is_president || !panel.portfolio) return null;

  return (
    <div className="flex items-center gap-2.5 border-t border-warning-soft bg-warning-soft px-7 py-2 text-[13px]">
      <Lock className="size-3.5 shrink-0 text-warning" />
      <b>Você governa: sua carteira está congelada até {displayShortDate(panel.portfolio.frozen_until)}.</b>
      <span className="text-muted-foreground">Comprar e vender ficam bloqueados; a sala vê o que você tem.</span>
    </div>
  );
}
