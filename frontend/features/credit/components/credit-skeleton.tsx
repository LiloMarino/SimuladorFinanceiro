import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto no formato da tela: faixa de números, nota de risco, oferta e tabela. */
export function CreditSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando o crédito">
      <Card>
        <CardContent>
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
            {[0, 1, 2, 3].map((item) => (
              <div key={item} className="grid gap-2">
                <Skeleton className="h-2.5 w-1/2" />
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-2.5 w-2/3" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      <div className="grid items-start gap-5 xl:grid-cols-[1fr_1.3fr]">
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
      <Skeleton className="h-48" />
    </div>
  );
}
