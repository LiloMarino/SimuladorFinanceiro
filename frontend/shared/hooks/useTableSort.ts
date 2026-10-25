import { useState } from "react";
import { nextTableSort, sortTableRows, type SortColumns, type TableSort } from "@/shared/lib/table-sort";

export function useTableSortState<K extends string>(defaultSort: TableSort<K> | null = null) {
  const [selected, setSort] = useState<TableSort<K> | null>(null);
  const sort = selected ?? defaultSort;
  return {
    sort,
    setSort,
    header: (column: K) => ({
      direction: sort?.column === column ? sort.direction : undefined,
      onSort: () => setSort((previous) => nextTableSort(previous ?? defaultSort, column)),
    }),
  };
}

export function useTableSort<T, K extends string>(
  rows: readonly T[],
  columns: SortColumns<T, K>,
  defaultSort: TableSort<NoInfer<K>> | null = null,
) {
  const sorting = useTableSortState<K>(defaultSort);
  return { ...sorting, rows: sortTableRows(rows, columns, sorting.sort) };
}
