import { Database } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorState } from "@/shared/components/error-state";
import { CorrelationTool } from "../components/correlation-tool";
import { useCorrelationAssets } from "../hooks/queries/useCorrelationAssets";

export default function CorrelationPage() {
  const { data, isLoading, error, refetch } = useCorrelationAssets();

  if (isLoading) return <Skeleton className="h-96" />;

  if (!data) {
    return (
      <Card>
        <CardContent>
          <ErrorState
            title="Não deu pra carregar os ativos"
            description="Confira se o servidor do host está ligado e tente de novo."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-5">
      {/* Fora da partida não há topo do app: a tela traz o próprio título */}
      {!data.end_fixed && (
        <header className="grid gap-1">
          <h1 className="text-2xl font-bold">Correlação entre ativos</h1>
          <p className="text-muted-foreground">
            Fora da partida você escolhe a data final; dentro dela, a data é a da simulação.
          </p>
        </header>
      )}

      {data.last_date ? (
        <CorrelationTool assets={data.assets} lastDate={data.last_date} endFixed={data.end_fixed} />
      ) : (
        <Card>
          <CardContent>
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Database />
                </EmptyMedia>
                <EmptyTitle>Nenhum ativo com preço na base</EmptyTitle>
                <EmptyDescription>
                  A correlação usa os preços históricos. Importe ações na Central de dados (só fora da partida).
                </EmptyDescription>
              </EmptyHeader>
              {!data.end_fixed && (
                <EmptyContent>
                  <Button nativeButton={false} render={<Link to="/import-assets" />}>
                    Abrir Central de dados
                  </Button>
                </EmptyContent>
              )}
            </Empty>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
