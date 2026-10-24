import { useNavigate } from "react-router-dom";
import { CalendarDays, FlaskConical, GitCompareArrows, Grid3x3, List, type LucideIcon } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { isOutdatedStock } from "@/shared/lib/series-coverage";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { useBacktestStatus } from "@/shared/hooks/queries/useBacktestStatus";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";

type Tool = {
  icon: LucideIcon;
  title: string;
  description: string;
  onClick: () => void;
  badge?: { text: string; variant: "secondary" | "warning" | "info" };
  /** Por que a ferramenta está bloqueada agora; sem isso ela abre normalmente */
  lockedBecause?: string;
};

/** Ferramentas de fora da partida, com contadores do que pede atenção. */
export function OfflineTools({ onOpenSaved, isHost }: { onOpenSaved: () => void; isHost: boolean }) {
  const navigate = useNavigate();
  const { simulation } = useSimulation();
  const { data: backtest } = useBacktestStatus();
  const { data: saved } = useSimulationList();
  const { data: coverage } = useSeriesCoverage();

  const savedCount = saved?.length ?? 0;
  const outdatedCount = (coverage ?? []).filter(isOutdatedStock).length;
  const backtestRunning = !!backtest?.progress;

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
      onClick: () => void navigate("/compare-simulations"),
    },
    {
      icon: CalendarDays,
      title: "Central de dados",
      description: "Importe ações e atualize indicadores",
      onClick: () => void navigate("/import-assets"),
      badge: outdatedCount
        ? { text: `${outdatedCount} ${outdatedCount === 1 ? "desatualizada" : "desatualizadas"}`, variant: "warning" }
        : undefined,
      lockedBecause: backtestRunning ? "Disponível quando o backtest terminar" : undefined,
    },
    {
      icon: FlaskConical,
      title: "Testar estratégias",
      description: "Rode estratégias sobre anos de mercado sem esperar o jogo. Só o host roda.",
      onClick: () => void navigate("/backtest/new"),
      badge: { text: "Backtest", variant: "info" },
      lockedBecause: !isHost
        ? "Só o host roda backtest"
        : simulation?.active
          ? "Há uma partida em andamento"
          : undefined,
    },
    {
      icon: Grid3x3,
      title: "Correlação entre ativos",
      description: "Veja quais ações andam juntas",
      onClick: () => void navigate("/correlation"),
    },
  ];

  return (
    <section className="grid gap-2.5">
      <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
        Fora da partida
      </span>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {tools.map(({ icon: Icon, title, description, onClick, badge, lockedBecause }) => (
          <button
            key={title}
            type="button"
            onClick={onClick}
            disabled={!!lockedBecause}
            title={lockedBecause}
            className="flex items-start gap-3 rounded-xl border border-border bg-card px-4 py-3.5 text-left transition-colors hover:bg-subtle disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:bg-card"
          >
            <span className="flex size-[34px] shrink-0 items-center justify-center rounded-lg bg-info-soft text-primary">
              <Icon className="size-4" />
            </span>
            <span className="grid gap-0.5">
              <b className="font-semibold">{title}</b>
              <span className="text-xs text-muted-foreground">{lockedBecause ?? description}</span>
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
