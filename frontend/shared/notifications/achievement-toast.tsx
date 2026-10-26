import { AchievementIcon } from "@/shared/components/achievement-icon";
import type { AchievementUnlockedEvent } from "@/types";

type AchievementToastProps = {
  achievements: AchievementUnlockedEvent["achievements"];
  onSeeAll: () => void;
};

/** Conteúdo do aviso de conquista: uma só mostra nome e descrição, várias no mesmo dia viram uma lista. */
export function AchievementToast({ achievements, onSeeAll }: AchievementToastProps) {
  const [first] = achievements;
  if (!first) return null;

  const several = achievements.length > 1;

  return (
    <div className="relative flex w-[380px] max-w-full items-center gap-3.5 overflow-hidden rounded-xl bg-toast py-3.5 pr-4 pl-3.5 text-toast-foreground shadow-[0_12px_32px_rgba(15,23,41,.28)] before:absolute before:inset-y-0 before:left-0 before:w-[3px] before:bg-toast-warning">
      <AchievementIcon name={first.icon} state="unlocked" size="lg" onDark />
      <div className="grid min-w-0 flex-1 gap-0.5">
        <span className="text-[11px] font-semibold tracking-[.08em] text-toast-warning uppercase">
          {several
            ? `${achievements.length} conquistas no mesmo dia`
            : first.secret
              ? "Conquista secreta revelada"
              : "Conquista desbloqueada"}
        </span>
        {several ? (
          <ul className="grid gap-0.5 text-sm font-semibold">
            {achievements.map((a) => (
              <li key={a.code} className="truncate" title={a.name}>
                {a.name}
              </li>
            ))}
          </ul>
        ) : (
          <>
            <strong className="truncate text-sm leading-[1.3] font-semibold">{first.name}</strong>
            <span className="line-clamp-2 text-[12.5px] leading-[1.4] text-toast-muted">{first.description}</span>
          </>
        )}
        {several && (
          <button
            type="button"
            className="mt-1 self-start text-xs font-semibold text-toast-info hover:underline"
            onClick={onSeeAll}
          >
            {achievements.length === 2 ? "Ver as duas" : "Ver todas"}
          </button>
        )}
      </div>
    </div>
  );
}
