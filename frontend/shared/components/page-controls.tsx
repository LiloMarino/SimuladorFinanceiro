import { Button } from "@/shared/components/ui/button";
import type { PagedRows } from "@/shared/hooks/usePagedRows";

type PageControlsProps = { paging: PagedRows<unknown>; unit: string };

/** O contador "1–6 de 14 meses" e os botões Anterior e Próxima de uma lista paginada. */
export function PageControls({ paging, unit }: PageControlsProps) {
  if (!paging.paged) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground">
        {paging.from + 1}–{paging.from + paging.shown.length} de {paging.total} {unit}
      </span>
      <Button size="xs" variant="outline" disabled={!paging.hasPrevious} onClick={paging.previous}>
        Anterior
      </Button>
      <Button size="xs" variant="outline" disabled={!paging.hasNext} onClick={paging.next}>
        Próxima
      </Button>
    </div>
  );
}
