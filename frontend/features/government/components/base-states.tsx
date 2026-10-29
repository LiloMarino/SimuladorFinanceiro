import { RefreshCw, TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto no formato do hemiciclo e da tabela da base. */
export function BaseSkeleton() {
  return (
    <Card aria-busy="true" aria-label="Carregando a base do governo">
      <CardContent>
        <div className="grid gap-4">
          <h2 className="text-[15px] font-semibold">Base no Congresso</h2>
          <div className="flex items-end gap-4">
            <Skeleton className="h-25 w-50" />
            <div className="grid flex-1 gap-2">
              <Skeleton className="h-11.5" />
              <Skeleton className="h-11.5" />
            </div>
          </div>
          <Skeleton className="h-3.5 w-[70%]" />
        </div>
      </CardContent>
    </Card>
  );
}

/** Falha só no card da base: o resto do Governo continua funcionando. */
export function BaseError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <h2 className="text-[15px] font-semibold">Base no Congresso</h2>
          <Alert variant="destructive">
            <TriangleAlert />
            <AlertTitle>Não deu para carregar a base.</AlertTitle>
            <AlertDescription>
              O resto do Governo continua funcionando. Os acordos seguem valendo enquanto isso.
            </AlertDescription>
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
