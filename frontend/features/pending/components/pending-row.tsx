import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type { Pending } from "@/types";
import { pendingTarget } from "../lib/pending";

type PendingRowProps = {
  item: Pending;
  onAct: (item: Pending) => void;
};

/** Uma pendência: título, o que a causa, quando ela some e o botão da ação que a resolve. */
export function PendingRow({ item, onAct }: PendingRowProps) {
  const target = pendingTarget(item);

  return (
    <li
      className={cn(
        "flex items-center gap-2.5 border-t border-l-3 py-2.5 pr-3 pl-3.25",
        item.severity === "SEVERE" ? "border-l-destructive" : "border-l-warning",
      )}
    >
      <div className="grid min-w-0 flex-1 gap-px">
        <b className="text-[13px] font-semibold">{item.title}</b>
        <span className="truncate text-xs text-muted-foreground" title={item.detail}>
          {item.detail}
        </span>
        <span className="text-[11px] text-muted-foreground/80">{item.resolves}</span>
      </div>
      <Button variant="outline" size="xs" onClick={() => onAct(item)}>
        {target.label}
      </Button>
    </li>
  );
}
