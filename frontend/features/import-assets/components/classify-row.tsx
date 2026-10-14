import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { TableCell, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { Sector, SeriesCoverage, StockSegment } from "@/types";

const NEW_SECTOR = "__new__";

type ClassifyRowProps = {
  series: SeriesCoverage;
  columns: number;
  onClose: () => void;
};

/** Classificação aberta na própria linha da tabela, com os setores que já existem em chips. */
export function ClassifyRow({ series, columns, onClose }: ClassifyRowProps) {
  const queryClient = useQueryClient();
  const { data: sectors } = useApiQuery({
    queryKey: queryKeys.sectors(),
    queryFn: ({ signal }) => apiFetch<Sector[]>("/api/import-assets/sectors", { signal }),
  });
  const { data: suggestion } = useApiQuery({
    queryKey: queryKeys.segmentSuggestion(series.key),
    queryFn: ({ signal }) =>
      apiFetch<StockSegment | null>(`/api/import-assets/stocks/${series.key}/suggestion`, { signal }),
    staleTime: Infinity,
  });

  const known = sectors?.map((s) => s.name) ?? [];
  const current = series.segment;
  const [sectorChoice, setSectorChoice] = useState(
    current && !known.includes(current.sector) && known.length ? NEW_SECTOR : (current?.sector ?? ""),
  );
  const [newSector, setNewSector] = useState(current?.sector ?? "");
  const [segment, setSegment] = useState(current?.segment ?? "");

  const sector = sectorChoice === NEW_SECTOR ? newSector.trim() : sectorChoice;
  const segmentOptions = sectors?.find((s) => s.name === sector)?.segments ?? [];

  const onSettled = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.sectors() });
  };
  const save = useApiMutation({
    mutationFn: (body: StockSegment) =>
      apiFetch(`/api/import-assets/stocks/${series.key}/segment`, { method: "PUT", body }),
    onSuccess: onClose,
    onError: (err) => toastApiError(err),
    onSettled,
  });
  const remove = useApiMutation({
    mutationFn: () => apiFetch(`/api/import-assets/stocks/${series.key}/segment`, { method: "DELETE" }),
    onSuccess: onClose,
    onError: (err) => toastApiError(err),
    onSettled,
  });

  const applySuggestion = (s: StockSegment) => {
    setSectorChoice(known.includes(s.sector) ? s.sector : NEW_SECTOR);
    setNewSector(s.sector);
    setSegment(s.segment);
  };

  const busy = save.isPending || remove.isPending;
  const datalistId = `segments-${series.key}`;

  return (
    <TableRow variant="editing">
      <TableCell colSpan={columns}>
        <div className="grid gap-3 py-1 whitespace-normal">
          {/* Setor */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="w-16 text-xs font-medium text-muted-foreground">Setor</span>
            <ToggleGroup
              variant="outline"
              size="sm"
              aria-label="Setor"
              value={sectorChoice ? [sectorChoice] : []}
              onValueChange={(values) => setSectorChoice(values[0] ?? "")}
              className="flex-wrap"
            >
              {known.map((name) => (
                <ToggleGroupItem key={name} value={name}>
                  {name}
                </ToggleGroupItem>
              ))}
              <ToggleGroupItem value={NEW_SECTOR}>
                <Plus />
                Novo
              </ToggleGroupItem>
            </ToggleGroup>
            {sectorChoice === NEW_SECTOR && (
              <Input
                aria-label="Nome do setor novo"
                value={newSector}
                onChange={(e) => setNewSector(e.target.value)}
                placeholder="Nome do setor"
                className="w-56"
              />
            )}
          </div>

          {/* Segmento */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="w-16 text-xs font-medium text-muted-foreground">Segmento</span>
            <Input
              aria-label="Segmento"
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
              list={datalistId}
              className="w-64"
            />
            <datalist id={datalistId}>
              {segmentOptions.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>
            {suggestion && (
              <span className="text-xs text-muted-foreground">
                Sugestão do yFinance: {suggestion.sector} · {suggestion.segment}{" "}
                <Button variant="link" size="xs" onClick={() => applySuggestion(suggestion)}>
                  Usar
                </Button>
              </span>
            )}
          </div>

          {/* Ações */}
          <div className="flex justify-end gap-2">
            {current && (
              <Button variant="ghost" size="sm" disabled={busy} onClick={() => remove.mutate()}>
                Tirar classificação
              </Button>
            )}
            <Button variant="ghost" size="sm" disabled={busy} onClick={onClose}>
              Cancelar
            </Button>
            <Button
              size="sm"
              disabled={busy || !sector || !segment.trim()}
              onClick={() => save.mutate({ sector, segment: segment.trim() })}
            >
              Salvar
            </Button>
          </div>
        </div>
      </TableCell>
    </TableRow>
  );
}
