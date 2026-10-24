import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ErrorState } from "@/shared/components/error-state";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import type { BacktestSetup } from "@/types";
import { BacktestForm } from "../components/backtest-form";
import { useBacktestSetup } from "../hooks/queries/useBacktestSetup";
import { formValues, setupStartDate } from "../lib/form";

const backToLobby = (
  <Button variant="outline" nativeButton={false} render={<Link to="/lobby" />}>
    Voltar ao lobby
  </Button>
);

/** Novo backtest: o período, o dinheiro e as estratégias que jogam o mesmo mercado sem esperar. */
export default function BacktestNewPage() {
  const [params] = useSearchParams();
  const fromParam = Number(params.get("from"));
  const from = Number.isInteger(fromParam) && fromParam > 0 ? fromParam : undefined;
  const { data: setup, error, refetch } = useBacktestSetup(from);

  return (
    <div className="grid gap-5">
      {/* Cabeçalho */}
      <div className="grid justify-items-start gap-3">
        {backToLobby}
        <div className="grid gap-1">
          <h1 className="text-2xl font-bold">Novo backtest</h1>
          <p className="text-sm text-muted-foreground">
            Escolha o período, o dinheiro e as estratégias. Todas jogam o mesmo mercado, dia a dia, sem esperar.
          </p>
        </div>
      </div>

      {error && !setup ? (
        <ErrorState
          title="Não conseguimos preparar o backtest"
          description="Só o host roda backtest, e o servidor precisa responder para mostrar até onde há mercado."
          error={error}
          onRetry={() => void refetch()}
        />
      ) : setup ? (
        <WithStrategies setup={setup} />
      ) : (
        <FormSkeleton />
      )}
    </div>
  );
}

/** Resolve as estratégias na data de início da configuração: o formulário só monta com elas prontas. */
function WithStrategies({ setup }: { setup: BacktestSetup }) {
  const startDate = setupStartDate(setup);
  const { data: strategies, error, refetch } = useBotStrategies(startDate);
  const values = useMemo(() => (strategies ? formValues(setup, strategies) : null), [setup, strategies]);

  if (error && !strategies) {
    return (
      <ErrorState
        title="Não deu para carregar as estratégias"
        description="Sem a lista, não dá para escolher o que o backtest roda."
        error={error}
        onRetry={() => void refetch()}
      >
        {backToLobby}
      </ErrorState>
    );
  }
  if (!strategies || !values) return <FormSkeleton />;

  return <BacktestForm setup={setup} strategies={strategies} values={values} startDate={startDate} />;
}

function FormSkeleton() {
  return (
    <div className="grid grid-cols-[360px_minmax(0,1fr)] gap-5" aria-busy="true" aria-label="Carregando o backtest">
      <div className="grid gap-3.5 rounded-xl border bg-card p-5">
        <Skeleton className="h-3.5 w-2/5" />
        <Skeleton className="h-10" />
        <div className="grid grid-cols-2 gap-2.5">
          <Skeleton className="h-10" />
          <Skeleton className="h-10" />
        </div>
        <Skeleton className="h-7" />
        <div className="grid grid-cols-2 gap-2.5">
          <Skeleton className="h-10" />
          <Skeleton className="h-10" />
        </div>
      </div>
      <div className="grid content-start gap-3 rounded-xl border bg-card p-5">
        {Array.from({ length: 3 }, (_, i) => (
          <div key={i} className="flex items-center gap-3 rounded-[10px] border p-2.5">
            <Skeleton circle className="size-9" />
            <div className="grid flex-1 gap-1.5">
              <Skeleton className="h-3 w-1/2" />
              <Skeleton className="h-2.5 w-4/5" />
            </div>
          </div>
        ))}
        <p className="text-xs text-muted-foreground">
          O formulário vem preenchido com a última configuração usada; as estratégias e os parâmetros chegam junto.
        </p>
      </div>
    </div>
  );
}
