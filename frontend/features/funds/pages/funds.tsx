import { Landmark } from "lucide-react";
import { Link, Navigate } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useAuth } from "@/shared/hooks/useAuth";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { FundRoomList } from "../components/fund-room-list";
import { useFunds } from "../hooks/queries/useFunds";

/** Sem gestora: o convite para fundar e as gestoras da sala. Com gestora, abre a página dela. */
export default function FundsPage() {
  usePageLabel("Gestoras");
  const { user } = useAuth();
  const { data: funds, error, refetch } = useFunds();

  if (!funds) {
    return (
      <CardState
        bare
        label="Carregando as gestoras"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar as gestoras"
      >
        <Skeleton className="h-32" />
        <Skeleton className="h-72" />
      </CardState>
    );
  }

  const mine = funds.find((fund) => fund.manager_user_id === user?.id);
  if (mine) return <Navigate to={`/funds/${mine.id}`} replace />;

  return (
    <>
      {/* Convite para fundar */}
      <Card variant="info">
        <CardContent>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <Landmark className="mt-0.5 size-5 shrink-0 text-fund" />
              <div className="grid gap-1">
                <h1 className="text-lg font-semibold">Funde a sua gestora</h1>
                <p className="max-w-2xl text-[13px] text-muted-foreground">
                  Você leva caixa e ações da sua carteira, recebe cotas e cobra taxas de quem entra. A sala compra suas
                  cotas numa oferta pública, e o preço de cada gestora pode ficar acima ou abaixo do que ela vale: é o
                  ágio.
                </p>
              </div>
            </div>
            <Button variant="fund" nativeButton={false} render={<Link to="/funds/new" />}>
              Fundar minha gestora
            </Button>
          </div>
        </CardContent>
      </Card>

      <FundRoomList funds={funds} />
    </>
  );
}
