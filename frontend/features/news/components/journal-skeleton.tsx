import { Skeleton } from "@/shared/components/ui/skeleton";

/** Três dias de manchetes em esboço, enquanto o histórico carrega. */
export function JournalSkeleton() {
  return (
    <div className="grid gap-6 pt-5" aria-busy="true" aria-label="Carregando o jornal">
      {[0, 1, 2].map((day) => (
        <div key={day} className="grid gap-3">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-6 w-full max-w-xl" />
          <Skeleton className="h-4 w-full max-w-md" />
        </div>
      ))}
    </div>
  );
}
