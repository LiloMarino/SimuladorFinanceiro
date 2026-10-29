import { RefreshCw, TriangleAlert } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** O título do orçamento com a etiqueta de que a sala inteira vê. */
function BudgetTitle() {
  return (
    <div className="flex items-center gap-2">
      <h2 className="text-[15px] font-semibold">Orçamento do governo</h2>
      <Badge variant="secondary" size="sm">
        a sala vê
      </Badge>
    </div>
  );
}

/** Esqueleto no formato do orçamento: os quatro números e o gráfico. */
export function BudgetSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando o orçamento">
      <Card>
        <CardContent>
          <div className="grid gap-4">
            <BudgetTitle />
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
            </div>
          </div>
        </CardContent>
      </Card>
      <div className="grid gap-5 xl:grid-cols-2">
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
    </div>
  );
}

/** Falha só no orçamento: o resto do Governo continua funcionando. */
export function BudgetError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <BudgetTitle />
          <Alert variant="destructive">
            <TriangleAlert />
            <AlertTitle>Não deu para carregar o orçamento.</AlertTitle>
            <AlertDescription>
              A partida segue normal; a conta do governo continua sendo feita a cada fechamento de mês.
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
