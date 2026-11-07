import * as React from "react";
import { cn } from "@/shared/lib/utils";

/** A tecla de atalho ao lado de um rótulo. */
function Kbd({ className, ...props }: React.ComponentProps<"kbd">) {
  return (
    <kbd
      data-slot="kbd"
      className={cn(
        "ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-sm border border-border bg-card px-1 font-mono text-xs font-medium text-muted-foreground select-none",
        className,
      )}
      {...props}
    />
  );
}

export { Kbd };
