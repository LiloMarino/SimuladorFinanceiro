import { RefreshCw, TriangleAlert } from "lucide-react";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto no formato da tela: cabeçalho, popularidade com impostos e a fila com a carteira. */
export function GovernmentSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando o governo">
      <Skeleton className="h-24" />
      <div className="grid gap-5 xl:grid-cols-2">
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.9fr)_minmax(0,1fr)]">
        <Skeleton className="h-64" />
        <Skeleton className="h-64" />
      </div>
    </div>
  );
}

/** Antes da primeira posse: o computador governa e os impostos ficam como estão. */
export function BeforeFirstTerm() {
  return (
    <Card>
      <CardContent>
        <Empty>
          <ExpansionEmblem expansion="government" size="lg" />
          <EmptyHeader>
            <EmptyTitle>O computador governa até a primeira posse</EmptyTitle>
            <EmptyDescription>
              Antes da posse ninguém propõe medidas e os impostos seguem como estão. Quem vencer a eleição passa a
              governar: propõe mudanças de imposto ao Congresso, acompanha a aprovação e, em troca, fica com a carteira
              congelada.
            </EmptyDescription>
          </EmptyHeader>
          <Badge variant="secondary">Governo do computador até a posse</Badge>
        </Empty>
      </CardContent>
    </Card>
  );
}

/** Falha ao carregar o governo: o que houve, com a ação de tentar de novo ao lado. */
export function GovernmentError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>Não deu para carregar o governo</AlertTitle>
          <AlertDescription>
            A conexão com a partida caiu. Impostos, medidas e votos seguem valendo; nada mudou fora da data.
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
