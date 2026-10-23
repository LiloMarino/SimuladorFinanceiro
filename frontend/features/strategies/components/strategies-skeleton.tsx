import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto no formato da página: cartão de modo, lista de estratégias e detalhe. */
export function StrategiesSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando as estratégias">
      <Card>
        <CardContent>
          <div className="flex items-center gap-5">
            <Skeleton className="h-13 w-55" />
            <div className="grid flex-1 gap-2">
              <Skeleton className="h-3.5 w-3/5" />
              <Skeleton className="h-3 w-4/5" />
            </div>
          </div>
        </CardContent>
      </Card>
      <div className="grid items-start gap-5 xl:grid-cols-[340px_minmax(0,1fr)]">
        <Card size="sm">
          <CardContent>
            <div className="grid gap-3">
              {[0, 1, 2, 3, 4].map((item) => (
                <Skeleton key={item} className="h-9 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <div className="grid gap-3">
              <Skeleton className="h-4 w-2/5" />
              <Skeleton className="h-3 w-4/5" />
              <Skeleton className="h-3 w-3/5" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
