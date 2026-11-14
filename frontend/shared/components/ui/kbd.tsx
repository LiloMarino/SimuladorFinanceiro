import * as React from "react";
import { cn } from "@/shared/lib/utils";

/** A tecla de atalho ao lado de um rótulo; `pressed` a acende enquanto a tecla está segura; `inverse` é a tecla dentro de uma dica escura. */
function Kbd({
  className,
  pressed,
  inverse,
  ...props
}: React.ComponentProps<"kbd"> & { pressed?: boolean; inverse?: boolean }) {
  return (
    <kbd
      data-slot="kbd"
      data-pressed={pressed || undefined}
      className={cn(
        "ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-sm border border-border bg-card px-1 font-mono text-xs font-medium text-muted-foreground select-none data-pressed:border-info data-pressed:bg-info-soft data-pressed:text-info",
        inverse && "ml-0 border-sidebar-accent bg-sidebar-accent text-sidebar-accent-foreground",
        className,
      )}
      {...props}
    />
  );
}

export { Kbd };
