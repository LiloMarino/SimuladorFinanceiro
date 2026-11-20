import { useState } from "react";

export type PagedRows<T> = {
  /** A fatia da página atual. */
  shown: T[];
  /** Posição (a partir de 0) da primeira linha da fatia. */
  from: number;
  total: number;
  /** Mais de uma página: os botões só aparecem quando há para onde ir. */
  paged: boolean;
  hasPrevious: boolean;
  hasNext: boolean;
  previous: () => void;
  next: () => void;
};

/** Divide a lista em páginas de `pageSize` linhas; a página se mantém dentro do que a lista comporta. */
export function usePagedRows<T>(rows: T[], pageSize: number): PagedRows<T> {
  const [page, setPage] = useState(0);
  const pages = Math.max(1, Math.ceil(rows.length / pageSize));
  const current = Math.min(page, pages - 1);
  const from = current * pageSize;

  return {
    shown: rows.slice(from, from + pageSize),
    from,
    total: rows.length,
    paged: rows.length > pageSize,
    hasPrevious: current > 0,
    hasNext: current < pages - 1,
    previous: () => setPage(current - 1),
    next: () => setPage(current + 1),
  };
}
