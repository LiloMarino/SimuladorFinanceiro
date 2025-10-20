import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
} from "@/components/ui/alert-dialog";
import CSVForm, { type CsvFormData } from "@/components/import-assets/csv-form";
import YFinanceForm, { type YFinanceFormData } from "@/components/import-assets/yfinance-form";
import { useMutationApi } from "@/hooks/useMutationApi";
import { useFormDataMutation } from "@/hooks/useFormDataMutation";
import { toast } from "sonner";

type ImportFormData = { type: "csv"; data: CsvFormData } | { type: "yfinance"; data: YFinanceFormData };

export default function ImportAssetsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [pendingImport, setPendingImport] = useState<ImportFormData | null>(null);

  const csvMutation = useFormDataMutation("/api/import-assets", {
    onSuccess: () => toast.success("Importação CSV concluída!"),
    onError: (err) => toast.error(err.message),
  });

  const yFinanceMutation = useMutationApi("/api/import-assets", {
    onSuccess: () => toast.success("Importação via YFinance concluída!"),
    onError: (err) => toast.error(err.message),
  });

  const handleConfirm = async () => {
    if (!pendingImport) return;

    switch (pendingImport.type) {
      case "csv": {
        setDialogOpen(false);
        const formData = new FormData();
        const { csv_file, ticker, overwrite } = pendingImport.data;
        formData.append("action", "csv");
        formData.append("ticker", ticker);
        formData.append("overwrite", String(overwrite ?? false));
        formData.append("csv_file", csv_file);
        await csvMutation.mutate(formData);
        break;
      }

      case "yfinance": {
        setDialogOpen(false);
        await yFinanceMutation.mutate({
          action: "yfinance",
          ticker: pendingImport.data.ticker,
          overwrite: pendingImport.data.overwrite ?? false,
        });
        break;
      }
    }
    setPendingImport(null);
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
