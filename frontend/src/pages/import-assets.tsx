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

type ImportFormData = { type: "csv"; data: CsvFormData } | { type: "yfinance"; data: YFinanceFormData };

export default function ImportAssetsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [pendingImport, setPendingImport] = useState<ImportFormData | null>(null);

  const handleConfirm = async () => {
    if (!pendingImport) return;

    switch (pendingImport.type) {
      case "csv":
        console.log("Enviando CSV:", pendingImport.data);
        // await uploadCsv(pendingImport.data)
        break;
      case "yfinance":
        console.log("Buscando via yFinance:", pendingImport.data);
        // await importFromYFinance(pendingImport.data)
        break;
    }
    setDialogOpen(false);
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
