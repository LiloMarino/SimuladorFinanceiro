import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Info, RefreshCw, Sparkles } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { TableCell, TableRow } from "@/shared/components/ui/table";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { Sector, SeriesCoverage, StockSegment } from "@/types";
import { SectorCombobox } from "./sector-combobox";

type ClassifyRowProps = {
  series: SeriesCoverage;
  columns: number;
  onClose: () => void;
};

/** Classificação aberta na própria linha da tabela: sugestão do yFinance no topo, setor e segmento lado a lado. */
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
  const [sector, setSector] = useState(current?.sector ?? "");
  const [segment, setSegment] = useState(current?.segment ?? "");

  const segmentOptions = sectors?.find((s) => s.name === sector)?.segments ?? [];
  const sectorId = `classify-sector-${series.key}`;
  const segmentId = `classify-segment-${series.key}`;
  const datalistId = `segments-${series.key}`;

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

  const refreshProfile = useApiMutation({
    mutationFn: () => apiFetch(`/api/import-assets/stocks/${series.key}/profile/refresh`, { method: "POST" }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.segmentSuggestion(series.key) }),
  });

  const busy = save.isPending || remove.isPending;

  const refreshButton = (
    <Button variant="ghost" size="sm" disabled={refreshProfile.isPending} onClick={() => refreshProfile.mutate()}>
      <RefreshCw data-icon="inline-start" />
      Atualizar perfil
    </Button>
  );

  return (
    <TableRow variant="editing">
      <TableCell colSpan={columns}>
        <div className="grid gap-4 py-2 whitespace-normal">
          {/* Sugestão do yFinance */}
          {suggestion ? (
            <div className="flex items-center gap-3 rounded-lg border border-info-border bg-card px-3 py-2">
              <Sparkles className="size-4 shrink-0 text-primary" />
              <span className="flex-1 text-[13px]">
                O yFinance sugere{" "}
                <b>
                  {suggestion.sector} › {suggestion.segment}
                </b>
              </span>
              {refreshButton}
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSector(suggestion.sector);
                  setSegment(suggestion.segment);
                }}
              >
                Usar sugestão
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-3 rounded-lg border border-dashed border-input px-3 py-2 text-[13px] text-muted-foreground">
              <Info className="size-4 shrink-0" />
              <span className="flex-1">O yFinance não sugeriu setor pra esse código. Escolha um ou crie.</span>
              {refreshButton}
            </div>
          )}

          {/* Setor e segmento */}
          <div className="grid grid-cols-2 gap-4">
            <Field>
              <FieldLabel htmlFor={sectorId}>Setor</FieldLabel>
              <SectorCombobox id={sectorId} sectors={known} value={sector} onChange={setSector} />
            </Field>
            <Field>
              <FieldLabel htmlFor={segmentId}>
                Segmento <span className="font-normal text-muted-foreground">· opcional</span>
              </FieldLabel>
              <Input id={segmentId} value={segment} onChange={(e) => setSegment(e.target.value)} list={datalistId} />
              <datalist id={datalistId}>
                {segmentOptions.map((name) => (
                  <option key={name} value={name} />
                ))}
              </datalist>
            </Field>
          </div>

          {/* Ações */}
          <div className="flex items-center justify-between gap-2">
            {current ? (
              <Button variant="link-destructive" size="sm" disabled={busy} onClick={() => remove.mutate()}>
                Tirar classificação
              </Button>
            ) : (
              <span />
            )}
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={busy} onClick={onClose}>
                Cancelar
              </Button>
              {/* A API pede segmento: sem ele, vale o próprio setor, como na sugestão do yFinance */}
              <Button
                size="sm"
                disabled={busy || !sector}
                onClick={() => save.mutate({ sector, segment: segment.trim() || sector })}
              >
                Salvar
              </Button>
            </div>
          </div>
        </div>
      </TableCell>
    </TableRow>
  );
}
