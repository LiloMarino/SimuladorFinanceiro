import { useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import type { Sector, SeriesCoverage } from "@/types";

const classifySchema = z.object({
  sector: z.string().trim().min(1, "Informe o setor"),
  segment: z.string().trim().min(1, "Informe o segmento"),
});

type ClassifyFormData = z.infer<typeof classifySchema>;

interface ClassifyStockDialogProps {
  series: SeriesCoverage;
  onClose: () => void;
}

export function ClassifyStockDialog({ series, onClose }: ClassifyStockDialogProps) {
  const queryClient = useQueryClient();
  const { data: sectors } = useApiQuery({
    queryKey: queryKeys.sectors(),
    queryFn: ({ signal }) => apiFetch<Sector[]>("/api/import-assets/sectors", { signal }),
  });

  const form = useForm<ClassifyFormData>({
    resolver: zodResolver(classifySchema),
    defaultValues: { sector: series.segment?.sector ?? "", segment: series.segment?.segment ?? "" },
  });

  const onSettled = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.sectors() });
  };
  const saveMutation = useApiMutation({
    mutationFn: (body: ClassifyFormData) =>
      apiFetch(`/api/import-assets/stocks/${series.key}/segment`, { method: "PUT", body }),
    onSuccess: onClose,
    onError: (err) => toast.error(err.message),
    onSettled,
  });
  const removeMutation = useApiMutation({
    mutationFn: () => apiFetch(`/api/import-assets/stocks/${series.key}/segment`, { method: "DELETE" }),
    onSuccess: onClose,
    onError: (err) => toast.error(err.message),
    onSettled,
  });

  // Sugere os segmentos do setor digitado; setor novo ainda não tem nenhum
  const typedSector = form.watch("sector").trim();
  const segmentSuggestions = sectors?.find((s) => s.name === typedSector)?.segments ?? [];
  const busy = saveMutation.isPending || removeMutation.isPending;

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Classificar {series.key}</DialogTitle>
          <DialogDescription>
            Escolha um setor e um segmento existentes ou digite nomes novos. A carteira e as estatísticas agrupam as
            ações por eles.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit((data) => saveMutation.mutate(data))} className="space-y-4">
            <FormField
              control={form.control}
              name="sector"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Setor</FormLabel>
                  <FormControl>
                    <Input list="sector-suggestions" placeholder="Ex: Financeiro" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="segment"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Segmento</FormLabel>
                  <FormControl>
                    <Input list="segment-suggestions" placeholder="Ex: Bancos" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <datalist id="sector-suggestions">
              {sectors?.map((s) => <option key={s.name} value={s.name} />)}
            </datalist>
            <datalist id="segment-suggestions">
              {segmentSuggestions.map((name) => (
                <option key={name} value={name} />
              ))}
            </datalist>

            <DialogFooter>
              {series.segment && (
                <Button type="button" variant="outline" disabled={busy} onClick={() => removeMutation.mutate()}>
                  Remover classificação
                </Button>
              )}
              <Button type="submit" disabled={busy}>
                Salvar
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
