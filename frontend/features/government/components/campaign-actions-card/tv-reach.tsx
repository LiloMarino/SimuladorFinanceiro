import { Progress } from "@/shared/components/ui/progress";
import { displayPercent } from "@/shared/lib/utils/display";
import type { VoterGroup } from "@/types";
import { GROUP_INFO } from "../../lib/voters";
import { ActionIcon } from "../campaign-action-icon";

/** A TV não escolhe grupo: o ganho vai a todos, na proporção do peso de cada um. */
export function TvReach({ weights }: { weights: Map<VoterGroup, string> }) {
  const rows = [...weights].sort((a, b) => Number(b[1]) - Number(a[1]));
  const top = Number(rows[0]?.[1] ?? 1);

  return (
    <div className="grid gap-3 rounded-[10px] border bg-subtle p-4">
      <div className="flex items-center gap-2.5 text-sm font-semibold">
        <ActionIcon kind="TV" />
        Atinge todos os grupos, pelo peso de cada um
      </div>
      <div className="grid gap-2">
        {rows.map(([group, weight]) => (
          <div key={group} className="grid grid-cols-[190px_minmax(0,1fr)_36px] items-center gap-2.5 text-[12.5px]">
            <span className="truncate">{GROUP_INFO[group].label}</span>
            <Progress value={(Number(weight) / top) * 100} size="sm" aria-label={GROUP_INFO[group].label} />
            <span className="text-right font-mono">{displayPercent(weight, 0)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
