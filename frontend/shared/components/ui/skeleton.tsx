import { cn } from "@/shared/lib/utils";

/** `circle`: o lugar de um ícone ou avatar. */
function Skeleton({ className, circle = false, ...props }: React.ComponentProps<"div"> & { circle?: boolean }) {
  return (
    <div
      data-slot="skeleton"
      className={cn("animate-pulse bg-muted", circle ? "rounded-full" : "rounded-md", className)}
      {...props}
    />
  );
}

export { Skeleton };
