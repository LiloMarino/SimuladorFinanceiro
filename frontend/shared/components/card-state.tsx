import { RefreshCw, TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import type ApiError from "@/shared/lib/models/ApiError";

type CardStateProps = {
  /** Título do cartão, igual nos dois estados */
  title?: React.ReactNode;
  /** O que o leitor de tela anuncia enquanto carrega */
  label: string;
  /** Sem erro, o cartão está carregando */
  error: ApiError | null | undefined;
  onRetry: () => void;
  errorTitle: string;
  /** Sem texto próprio, vale a mensagem do erro da API */
  errorDescription?: string;
  /** Sem cartão em volta no carregamento: o esqueleto traz o próprio formato (a tela inteira) */
  bare?: boolean;
  /** O formato do cartão carregado, em esqueleto */
  children: React.ReactNode;
};

/** O cartão que ainda não tem o dado: esqueleto enquanto carrega, aviso com "Tentar de novo" se falhou. O erro fica neste cartão. */
export function CardState({
  title,
  label,
  error,
  onRetry,
  errorTitle,
  errorDescription,
  bare = false,
  children,
}: CardStateProps) {
  if (error) {
    return (
      <Card>
        <CardContent>
          <div className="grid gap-3">
            {title && <h2 className="text-[15px] font-semibold">{title}</h2>}
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>{errorTitle}</AlertTitle>
              <AlertDescription>{errorDescription ?? error.message}</AlertDescription>
              <AlertAction>
                <Button size="xs" variant="outline" onClick={onRetry}>
                  <RefreshCw />
                  Tentar de novo
                </Button>
              </AlertAction>
            </Alert>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (bare) {
    return (
      <div className="grid gap-5" aria-busy="true" aria-label={label}>
        {children}
      </div>
    );
  }

  return (
    <Card aria-busy="true" aria-label={label}>
      <CardContent>
        <div className="grid gap-3">
          {title && <h2 className="text-[15px] font-semibold">{title}</h2>}
          {children}
        </div>
      </CardContent>
    </Card>
  );
}
