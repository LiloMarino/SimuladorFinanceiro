import { type VariantProps } from "class-variance-authority";
import { statusDotVariants, statusVariants } from "./variants/statusVariants";
import { cn } from "@/shared/lib/utils";

type StatusKind = NonNullable<VariantProps<typeof statusVariants>["status"]>;

// Bolinha de presença (padrão Status do Kibo UI): online pulsa, ausente e offline ficam paradas
function StatusIndicator({ status = "offline" }: { status?: StatusKind }) {
  return (
    <span data-slot="status-indicator" className="relative flex size-2 shrink-0" aria-hidden="true">
      {status === "online" && (
        <span className="absolute inline-flex size-full rounded-full bg-success opacity-75 motion-safe:animate-ping" />
      )}
      <span className={statusDotVariants({ status })} />
    </span>
  );
}

function Status({
  className,
  status = "offline",
  children,
  ...props
}: React.ComponentProps<"span"> & { status?: StatusKind }) {
  return (
    <span data-slot="status" data-status={status} className={cn(statusVariants({ status }), className)} {...props}>
      <StatusIndicator status={status} />
      {children}
    </span>
  );
}

export { Status, StatusIndicator };
