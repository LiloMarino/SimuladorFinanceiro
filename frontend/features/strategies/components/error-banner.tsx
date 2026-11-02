import { useState } from "react";
import { CircleAlert, Copy, Terminal } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { StrategyError } from "@/types";

type ErrorBannerProps = {
  error: StrategyError;
  /** Falso quando a estratégia que deu erro não está mais na lista */
  canRetry: boolean;
  onEditParams: () => void;
  onTurnOnAgain: () => void;
};

/** A estratégia deu erro e devolveu o jogador ao manual: a causa, o que fazer e o rastro técnico. */
export function ErrorBanner({ error, canRetry, onEditParams, onTurnOnAgain }: ErrorBannerProps) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    if (!error.traceback) return;
    await navigator.clipboard.writeText(error.traceback);
    setCopied(true);
  };

  return (
    <div className="grid gap-3.5">
      <Alert variant="destructive">
        <CircleAlert />
        <AlertTitle>Voltou ao manual em {displayDayMonth(error.error_date)}: a estratégia deu erro</AlertTitle>
        <AlertDescription>{error.message}</AlertDescription>
        {canRetry && (
          <AlertAction>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={onEditParams}>
                Mudar parâmetros
              </Button>
              <Button size="sm" onClick={onTurnOnAgain}>
                Ligar de novo
              </Button>
            </div>
          </AlertAction>
        )}
      </Alert>

      {error.traceback && (
        <Card size="sm">
          <CardContent>
            <div className="grid gap-2.5">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-sm font-medium">
                  <Terminal className="size-3.5" />
                  Detalhes técnicos
                </span>
                <Button variant="outline" size="xs" onClick={() => void copy()}>
                  <Copy />
                  {copied ? "Copiado" : "Copiar"}
                </Button>
              </div>
              <pre className="max-h-48 overflow-auto rounded-lg bg-subtle p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap text-secondary-foreground">
                {error.traceback}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
