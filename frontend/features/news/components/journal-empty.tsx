import { Newspaper, SearchX } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import type { JournalFilter } from "../lib/filter";

type JournalEmptyProps = {
  /** Quantas manchetes vieram do servidor, sem filtro */
  total: number;
  filter: JournalFilter;
  onClear: () => void;
};

/** O motivo de a página estar sem manchetes: filtro apertado, tipos desligados ou partida sem notícia. */
export function JournalEmpty({ total, filter, onClear }: JournalEmptyProps) {
  const filtered = filter.query.trim() !== "" || filter.section !== null || filter.onlyMine;
  return filtered ? <NoResults onClear={onClear} /> : <NoNews empty={total === 0} />;
}

function NoNews({ empty }: { empty: boolean }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Newspaper />
        </EmptyMedia>
        <EmptyTitle>{empty ? "Nenhuma manchete ainda" : "Nenhuma manchete para mostrar"}</EmptyTitle>
        <EmptyDescription>
          {empty
            ? "As notícias da partida aparecem aqui conforme os pregões passam."
            : "Os tipos de notícia estão desligados. Dá para religá-los em Configurações."}
        </EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}

function NoResults({ onClear }: { onClear: () => void }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <SearchX />
        </EmptyMedia>
        <EmptyTitle>Nenhuma manchete com esse filtro</EmptyTitle>
        <EmptyDescription>Ajuste a busca, a seção ou o filtro da carteira.</EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="outline" onClick={onClear}>
          Limpar filtros
        </Button>
      </EmptyContent>
    </Empty>
  );
}
