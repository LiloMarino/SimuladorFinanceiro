import { Skeleton } from "@/shared/components/ui/skeleton";

/** O formato da página da gestora enquanto carrega: cabeçalho, cinco números, gráfico e as seções. */
export function FundSkeleton() {
  return (
    <>
      <Skeleton className="h-20" />
      <Skeleton className="h-28" />
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
        <Skeleton className="h-80" />
        <Skeleton className="h-80" />
      </div>
      <div className="grid items-start gap-5 xl:grid-cols-2">
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
      </div>
    </>
  );
}
