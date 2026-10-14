import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CalendarDays, GitCompareArrows, Grid3x3, List, type LucideIcon } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { seriesCoverageOptions } from "@/shared/lib/queries/seriesCoverageOptions";
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";

type Tool = {
  icon: LucideIcon;
  title: string;
  description: string;
  onClick: () => void;
  badge?: { text: string; variant: "secondary" | "warning" };
};

/** Ferramentas de fora da partida, com contadores do que pede atenção. */
export function OfflineTools({ onOpenSaved }: { onOpenSaved: () => void }) {
  const navigate = useNavigate();
  const { data: saved } = useQuery(simulationListOptions());
  const { data: coverage } = useQuery(seriesCoverageOptions());

  const savedCount = saved?.length ?? 0;
  const outdatedCount = (coverage ?? []).filter(isOutdatedStock).length;

  const tools: Tool[] = [
    {
      icon: List,
      title: "Simulações salvas",
      description: "Continue uma partida antiga ou veja o resultado",
      onClick: onOpenSaved,
      badge: savedCount
        ? { text: `${savedCount} ${savedCount === 1 ? "salva" : "salvas"}`, variant: "secondary" }
        : undefined,
    },
    {
      icon: GitCompareArrows,
      title: "Comparar simulações",
      description: "Ponha partidas lado a lado",
      onClick: () => navigate("/compare-simulations"),
    },
    {
      icon: Grid3x3,
      title: "Correlação entre ativos",
      description: "Veja quais ações andam juntas",
      onClick: () => navigate("/correlation"),
    },
    {
      icon: CalendarDays,
      title: "Central de dados",
      description: "Importe ações e atualize indicadores",
      onClick: () => navigate("/import-assets"),
      badge: outdatedCount
        ? { text: `${outdatedCount} ${outdatedCount === 1 ? "desatualizada" : "desatualizadas"}`, variant: "warning" }
        : undefined,
    },
  ];

  return (
    <section className="grid gap-2.5">
      <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
        Fora da partida
      </span>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {tools.map(({ icon: Icon, title, description, onClick, badge }) => (
          <button
            key={title}
            type="button"
            onClick={onClick}
            className="flex items-start gap-3 rounded-xl border border-border bg-card px-4 py-3.5 text-left transition-colors hover:bg-subtle"
          >
            <span className="flex size-[34px] shrink-0 items-center justify-center rounded-lg bg-info-soft text-primary">
              <Icon className="size-4" />
            </span>
            <span className="grid gap-0.5">
              <b className="font-semibold">{title}</b>
              <span className="text-xs text-muted-foreground">{description}</span>
              {badge && (
                <Badge variant={badge.variant} size="sm" className="mt-1">
                  {badge.text}
                </Badge>
              )}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
