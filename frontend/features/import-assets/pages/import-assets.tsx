import { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
} from "@/shared/components/ui/alert-dialog";

import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useFormDataMutation } from "@/shared/hooks/useFormDataMutation";
import { toast } from "sonner";
import type { CsvFormData } from "@/features/import-assets/components/csv-form";
import type { YFinanceFormData } from "@/features/import-assets/components/yfinance-form";
import CSVForm from "@/features/import-assets/components/csv-form";
import YFinanceForm from "@/features/import-assets/components/yfinance-form";

type ImportFormData = { type: "csv"; data: CsvFormData } | { type: "yfinance"; data: YFinanceFormData };

export default function ImportAssetsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [pendingImport, setPendingImport] = useState<ImportFormData | null>(null);

  const csvMutation = useFormDataMutation("/api/import-assets");
  const yFinanceMutation = useMutationApi("/api/import-assets");

  const handleConfirm = async () => {
    if (!pendingImport) return;

    setDialogOpen(false);
    let toastId: string | number | undefined;

    try {
      // Mostra o toast de loading
      toastId = toast.loading(
        pendingImport.type === "csv" ? "Importando arquivo CSV..." : "Baixando dados via YFinance..."
      );

      if (pendingImport.type === "csv") {
        const { csv_file, ticker, overwrite } = pendingImport.data;
        await csvMutation.mutate({
          action: "csv",
          ticker,
          overwrite,
          csv_file,
        });
        toast.success("Importação CSV concluída!", { id: toastId });
      } else {
        await yFinanceMutation.mutate({
          action: "yfinance",
          ticker: pendingImport.data.ticker,
          overwrite: pendingImport.data.overwrite ?? false,
        });
        toast.success("Importação via YFinance concluída!", { id: toastId });
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao realizar a importação.", { id: toastId });
    } finally {
      setPendingImport(null);
    }
  };

  return (
    <section className="section-content p-4">
      {/* AlertDialog de confirmação */}
      <AlertDialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Importação</AlertDialogTitle>
            <AlertDialogDescription>
              Deseja realmente importar os dados selecionados?{" "}
              {pendingImport?.data.overwrite && "Essa ação pode sobrescrever informações existentes."}
            </AlertDialogDescription>
          </AlertDialogHeader>

          <AlertDialogFooter className="flex justify-end space-x-2 mt-4">
            <Button variant="blue" onClick={handleConfirm}>
              Sim
            </Button>
            <Button variant="secondary" onClick={() => setDialogOpen(false)}>
              Cancelar
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Formulários */}
      <div className="bg-white rounded-lg shadow p-6 space-y-8">
        <h2 className="text-xl font-semibold mb-6">Importar Ativos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <CSVForm
            onSubmit={(data) => {
              setPendingImport({ type: "csv", data });
              setDialogOpen(true);
            }}
          />
          <YFinanceForm
            onSubmit={(data) => {
              setPendingImport({ type: "yfinance", data });
              setDialogOpen(true);
            }}
          />
        </div>
      </div>
    </section>
  );
}
