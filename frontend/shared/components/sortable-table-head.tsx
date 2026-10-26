import type { ComponentProps, ReactNode } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { TableHead } from "./ui/table";
import { cn } from "@/shared/lib/utils";
import type { SortDirection } from "@/shared/lib/table-sort";

type Props = ComponentProps<typeof TableHead> & {
  label: string;
  direction?: SortDirection | undefined;
  onSort: () => void;
  hint?: ReactNode;
};

/** O botão aceita teclado; dicas ficam ao lado para não aninhar controles. */
export function SortableTableHead({ label, direction, onSort, hint, children, numeric, ...props }: Props) {
  const Icon = direction === "asc" ? ArrowUp : direction === "desc" ? ArrowDown : ArrowUpDown;
  const next = direction === "asc" ? "decrescente" : "crescente";
  return (
    <TableHead
      {...props}
      numeric={numeric}
      scope="col"
      aria-sort={direction === "asc" ? "ascending" : direction === "desc" ? "descending" : "none"}
    >
      <span className={cn("flex items-center gap-1", numeric && "justify-end")}>
        <button
          type="button"
          onClick={onSort}
          aria-label={`Ordenar por ${label}, ordem ${next}`}
          title={`Ordenar por ${label}, ordem ${next}`}
          className={cn(
            "inline-flex min-h-9 items-center gap-1 rounded-sm outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring",
            direction && "font-semibold text-foreground",
          )}
        >
          {label}
          <Icon className="size-3.5 shrink-0" aria-hidden="true" />
        </button>
        {hint}
      </span>
      {children}
    </TableHead>
  );
}
