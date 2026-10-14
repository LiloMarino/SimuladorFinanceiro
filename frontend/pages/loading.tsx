import { useEffect, useState } from "react";
import { BrandMark } from "@/shared/components/brand-mark";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { cn } from "@/shared/lib/utils";

const SLOW_AFTER_MS = 10_000;

type LoadingPageProps = {
  variant?: "page" | "fullscreen";
  /** A conexão já falhou: mostra a explicação sem esperar */
  failed?: boolean;
  onRetry?: () => void;
  className?: string;
};

export function LoadingPage({ variant = "page", failed = false, onRetry, className }: LoadingPageProps) {
  if (variant === "page") {
    return (
      <section className={cn("flex min-h-[60vh] items-center justify-center", className)}>
        <Spinner className="size-8 text-muted-foreground" />
      </section>
    );
  }

  return <ConnectingScreen failed={failed} onRetry={onRetry} />;
}

function ConnectingScreen({ failed, onRetry }: { failed: boolean; onRetry?: () => void }) {
  const [slow, setSlow] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), SLOW_AFTER_MS);
    return () => clearTimeout(timer);
  }, []);

  const showHelp = failed || slow;

  return (
    <section className="flex h-svh flex-col items-center justify-center gap-4">
      <BrandMark size="lg" />
      <span className="text-lg font-bold">FinSim</span>
      {showHelp ? (
        <div className="grid max-w-[360px] justify-items-center gap-3 text-center">
          <span className="font-semibold">Está demorando mais que o normal</span>
          <span className="text-[13px] text-muted-foreground">
            O servidor do host pode estar desligado ou fora da rede. Confira com quem criou a sala.
          </span>
          <Button variant="outline" onClick={onRetry ?? (() => window.location.reload())}>
            Tentar de novo
          </Button>
        </div>
      ) : (
        <>
          <span className="h-1 w-40 overflow-hidden rounded-full bg-muted">
            <span className="block h-full w-2/5 animate-pulse rounded-full bg-primary" />
          </span>
          <span className="text-muted-foreground">Conectando à sala…</span>
        </>
      )}
    </section>
  );
}
