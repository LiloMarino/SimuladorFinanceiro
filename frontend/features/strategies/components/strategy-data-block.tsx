import type { UseQueryResult } from "@tanstack/react-query";
import { ErrorState } from "@/shared/components/error-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type ApiError from "@/shared/lib/models/ApiError";
import type { StrategyViewData, StrategyViewKind } from "@/types";
import { AllocationBlock } from "./strategy-allocation";
import { RankingBlock } from "./strategy-ranking";

type StrategyDataBlockProps = {
  kind: Extract<StrategyViewKind, "ranking" | "allocation">;
  query: UseQueryResult<StrategyViewData, ApiError>;
};

/** O ranking ou a alocação da estratégia: esqueleto ao carregar, erro com nova tentativa e o bloco pronto. */
export function StrategyDataBlock({ kind, query }: StrategyDataBlockProps) {
  if (query.isError) {
    return (
      <ErrorState
        title="Não deu para carregar"
        description="O servidor não respondeu. Seus parâmetros continuam como estão."
        error={query.error}
        onRetry={() => void query.refetch()}
      />
    );
  }
  if (!query.data) return <DataBlockSkeleton kind={kind} />;

  const { ranking, allocation, errors } = query.data;
  if (Object.keys(errors).length > 0) {
    return (
      <div className="grid h-40 place-items-center rounded-lg bg-subtle text-sm text-muted-foreground">
        Corrija os parâmetros para ver o resultado.
      </div>
    );
  }
  if (ranking) return <RankingBlock ranking={ranking} />;
  if (allocation) return <AllocationBlock allocation={allocation} />;
  return null;
}

function DataBlockSkeleton({ kind }: Pick<StrategyDataBlockProps, "kind">) {
  return kind === "ranking" ? (
    <div className="grid gap-2" aria-busy="true" aria-label="Carregando o ranking">
      {[0, 1, 2, 3, 4].map((row) => (
        <Skeleton key={row} className="h-9 w-full" />
      ))}
    </div>
  ) : (
    <div className="grid gap-4" aria-busy="true" aria-label="Carregando a alocação">
      {[0, 1].map((item) => (
        <div key={item} className="grid gap-2">
          <Skeleton className="h-4 w-2/5" />
          <Skeleton className="h-2 w-full" />
          <Skeleton className="h-2 w-full" />
        </div>
      ))}
    </div>
  );
}
