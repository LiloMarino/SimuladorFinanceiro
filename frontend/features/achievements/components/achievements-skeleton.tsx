import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ROW_GRID } from "./achievement-row";

/** Linhas da lista no formato final, enquanto a resposta não chega. */
export function AchievementsListSkeleton() {
  return (
    <ul aria-hidden="true">
      {Array.from({ length: 5 }, (_, i) => (
        <li key={i} className={`${ROW_GRID} border-b border-muted py-3 last:border-b-0`}>
          <Skeleton className="size-10" />
          <div className="grid gap-1.5">
            <Skeleton className="h-3 w-[55%]" />
            <Skeleton className="h-2.5 w-[85%]" />
          </div>
          <Skeleton className="h-2.5 w-[70%]" />
          <Skeleton className="h-2.5 w-[60%] justify-self-end" />
        </li>
      ))}
    </ul>
  );
}

/** O painel lateral enquanto a resposta não chega: o total e as três mais perto de sair. */
export function AchievementsPanelSkeleton() {
  return (
    <div aria-hidden="true" className="grid gap-4">
      <Card>
        <CardContent>
          <div className="flex items-center gap-3.5">
            <Skeleton className="size-13" />
            <div className="grid flex-1 gap-1.5">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-2.5 w-32" />
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <Skeleton className="h-3.5 w-28" />
            {Array.from({ length: 3 }, (_, i) => (
              <div key={i} className="flex items-center gap-2.5">
                <Skeleton className="size-9" />
                <div className="grid flex-1 gap-1.5">
                  <Skeleton className="h-3 w-[60%]" />
                  <Skeleton className="h-1.5 w-full" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
