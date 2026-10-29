import { RefreshCw, TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto no formato da tela: a faixa de números, o gráfico e os cartões de crescimento e desemprego. */
export function EconomySkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando a economia">
      <Skeleton className="h-28" />
      <Skeleton className="h-96" />
      <div className="grid gap-5 lg:grid-cols-2">
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
    </div>
  );
}

/** Falha ao carregar a economia, com a ação de tentar de novo. */
export function EconomyError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>Não deu para carregar a economia</AlertTitle>
          <AlertDescription>
            A conexão com a partida caiu. A SELIC e a inflação seguem valendo na partida.
          </AlertDescription>
          <AlertAction>
            <Button size="xs" variant="outline" onClick={onRetry}>
              <RefreshCw />
              Tentar de novo
            </Button>
          </AlertAction>
        </Alert>
      </CardContent>
    </Card>
  );
}
