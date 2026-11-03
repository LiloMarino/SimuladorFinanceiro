import { useEffect, useRef } from "react";

type UseLoadMoreOnVisibleOptions = {
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => unknown;
  /** Muda a cada página acrescentada; as páginas que vêm do cache chegam sem `isFetchingNextPage` virar */
  pageCount?: number;
};

/**
 * Pede a próxima página de uma lista paginada quando o elemento sentinela (o `ref` devolvido,
 * posto no fim da lista) aparece na área rolável.
 * O observador nasce de novo a cada página que termina de carregar: se o sentinela
 * ainda estiver à vista, a página seguinte vem logo, até a lista passar da altura da tela.
 */
export function useLoadMoreOnVisible({
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  pageCount,
}: UseLoadMoreOnVisibleOptions) {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasNextPage || isFetchingNextPage) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) void fetchNextPage();
      },
      // Começa a carregar um pouco antes do fim, para a rolagem não bater no rodapé da lista
      { rootMargin: "160px" },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage, pageCount]);

  return sentinelRef;
}
