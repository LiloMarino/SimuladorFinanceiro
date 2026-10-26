import { AchievementIcon } from "@/shared/components/achievement-icon";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import type { Achievement } from "@/types";
import { CATEGORY_LABELS, displayProgressShort, progressFraction } from "../lib/format";

const NEAR_LIMIT = 3;

type AchievementsSidePanelProps = {
  achievements: Achievement[];
  /** A partida em andamento; fora dela não há "nesta partida" */
  currentSimulationId?: number | undefined;
};

/** Resumo ao lado da lista: o total, as três bloqueadas mais perto de sair e o placar por categoria. */
export function AchievementsSidePanel({ achievements, currentSimulationId }: AchievementsSidePanelProps) {
  const unlocked = achievements.filter((a) => a.unlock);
  const inThisMatch = unlocked.filter((a) => a.unlock?.simulation_id === currentSimulationId).length;

  // As bloqueadas com barra, da mais adiantada para a menos
  const nearby = achievements
    .flatMap((a) => (!a.unlock && a.progress && Number(a.progress.current) > 0 ? [{ ...a, progress: a.progress }] : []))
    .sort((a, b) => progressFraction(b.progress) - progressFraction(a.progress))
    .slice(0, NEAR_LIMIT);

  const categories = (Object.keys(CATEGORY_LABELS) as Achievement["category"][])
    .map((category) => {
      const inCategory = achievements.filter((a) => a.category === category);
      return { category, total: inCategory.length, unlocked: inCategory.filter((a) => a.unlock).length };
    })
    .filter((c) => c.total > 0);

  return (
    <aside className="grid content-start gap-4">
      {/* Total */}
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <div className="flex items-center gap-3.5">
              <AchievementIcon name="TROPHY" state="unlocked" size="lg" />
              <div className="grid">
                <span>
                  <span className="font-mono text-2xl font-semibold">{unlocked.length}</span>
                  <span className="text-muted-foreground"> de {achievements.length}</span>
                </span>
                <span className="text-xs text-muted-foreground">
                  desbloqueadas
                  {currentSimulationId !== undefined && ` · ${inThisMatch} nesta partida`}
                </span>
              </div>
            </div>
            <Progress value={(unlocked.length / achievements.length) * 100} size="md" indicatorTone="gold" />
          </div>
        </CardContent>
      </Card>

      {/* Perto de sair */}
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <h2 className="text-[15px] font-semibold">Perto de sair</h2>
            {nearby.length === 0 ? (
              <p className="text-[13px] text-muted-foreground">
                Sem nenhuma com progresso ainda. As primeiras barras aparecem quando você jogar.
              </p>
            ) : (
              nearby.map((a) => (
                <div key={a.code} className="flex items-center gap-2.5">
                  <AchievementIcon name={a.icon} state="locked" size="sm" />
                  <div className="grid min-w-0 flex-1 gap-1">
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="truncate text-[13px] font-medium" title={a.name ?? undefined}>
                        {a.name}
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        {displayProgressShort(a.progress)}
                      </span>
                    </div>
                    <Progress value={progressFraction(a.progress) * 100} size="sm" />
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Por categoria */}
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <h2 className="text-[15px] font-semibold">Por categoria</h2>
            {categories.map((c) => (
              <div key={c.category} className="grid gap-1.25">
                <div className="flex items-center justify-between text-[13px]">
                  <span>{CATEGORY_LABELS[c.category]}</span>
                  <span className="font-mono text-muted-foreground">
                    {c.unlocked}/{c.total}
                  </span>
                </div>
                <Progress value={(c.unlocked / c.total) * 100} size="sm" indicatorTone="gold" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <p className="text-xs text-muted-foreground">
        Ficam salvas no computador do host e valem em todas as partidas desta sala.
      </p>
    </aside>
  );
}
