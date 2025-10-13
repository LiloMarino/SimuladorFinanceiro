import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileCsv, faChartLine, faCloudUploadAlt, faSearch } from "@fortawesome/free-solid-svg-icons";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogFooter, DialogTitle } from "@/components/ui/dialog";

// -------------------------
// Zod Schemas
// -------------------------
const csvSchema = z.object({
  ticker: z.string().min(1, "Informe o nome do ativo"),
  csv_file: z.any().refine((file) => file instanceof File, "Selecione um arquivo CSV válido"),
  overwrite: z.boolean(),
});

const ySchema = z.object({
  ticker: z.string().min(1, "Informe o código do ativo"),
  overwrite: z.boolean(),
});

type CsvFormData = z.infer<typeof csvSchema>;
type YFormData = z.infer<typeof ySchema>;

// -------------------------
// Componente Principal
// -------------------------
export default function ImportAssetsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentAction, setCurrentAction] = useState<"csv" | "yfinance" | null>(null);

  // Forms separados
  const csvForm = useForm<CsvFormData>({
    resolver: zodResolver(csvSchema),
    defaultValues: { ticker: "", csv_file: null, overwrite: false },
  });

  const yForm = useForm<YFormData>({
    resolver: zodResolver(ySchema),
    defaultValues: { ticker: "", overwrite: false },
  });

  // Submissão final após confirmar
  const handleConfirm = async () => {
    const form = currentAction === "csv" ? csvForm : yForm;
    const values = form.getValues();

    // Você pode adaptar conforme o backend espera:
    const formData = new FormData();
    for (const [key, value] of Object.entries(values)) {
      formData.append(key, value as any);
    }
    formData.append("action", currentAction!);

    await fetch("/import-assets", {
      method: "POST",
      body: formData,
    });

    setDialogOpen(false);
    setCurrentAction(null);
  };

  return (
    <section id="import-assets" className="section-content p-4">
      {/* Modal de confirmação */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Importação</DialogTitle>
          </DialogHeader>
          <p className="text-gray-700 mb-4">Deseja realmente importar os dados selecionados?</p>
          <DialogFooter className="flex justify-end space-x-2">
            <Button onClick={handleConfirm}>Sim</Button>
            <Button variant="secondary" onClick={() => setDialogOpen(false)}>
              Cancelar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="bg-white rounded-lg shadow p-6 space-y-8">
        <h2 className="text-xl font-semibold mb-6">Importar Ativos</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* --- CSV FORM --- */}
          <Form {...csvForm}>
            <form
              onSubmit={csvForm.handleSubmit(() => {
                setCurrentAction("csv");
                setDialogOpen(true);
              })}
              className="border rounded-lg p-6 space-y-4"
            >
              <div className="flex items-center mb-4">
                <FontAwesomeIcon icon={faFileCsv} className="text-blue-500 text-2xl mr-3" />
                <h3 className="text-lg font-medium">Importar via CSV</h3>
              </div>
              <p className="text-gray-600 mb-4">Faça upload de um arquivo CSV com os dados históricos do ativo.</p>

              <FormField
                control={csvForm.control}
                name="ticker"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome do Ativo</FormLabel>
                    <FormControl>
                      <Input placeholder="Digite o nome do ativo" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={csvForm.control}
                name="csv_file"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Arquivo CSV</FormLabel>
                    <FormControl>
                      <div
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) => {
                          e.preventDefault();
                          const file = e.dataTransfer.files?.[0];
                          if (file) field.onChange(file);
                        }}
                        onClick={() => document.getElementById("csv-upload")?.click()}
                        className="border-2 border-dashed border-gray-300 rounded-md p-6 text-center cursor-pointer transition-colors"
                      >
                        <input
                          id="csv-upload"
                          type="file"
                          accept=".csv"
                          className="hidden"
                          onChange={(e) => e.target.files && field.onChange(e.target.files[0])}
                        />
                        <FontAwesomeIcon icon={faCloudUploadAlt} className="text-3xl text-gray-400 mb-2" />
                        <p className="text-sm text-gray-500">Arraste e solte ou clique para selecionar</p>
                        {field.value && <p className="mt-2 text-sm text-gray-700">{(field.value as File)?.name}</p>}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={csvForm.control}
                name="overwrite"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                    <FormLabel className="text-sm">Sobrescrever dados existentes</FormLabel>
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full">
                Importar CSV
              </Button>
            </form>
          </Form>

          {/* --- YFINANCE FORM --- */}
          <Form {...yForm}>
            <form
              onSubmit={yForm.handleSubmit(() => {
                setCurrentAction("yfinance");
                setDialogOpen(true);
              })}
              className="border rounded-lg p-6 space-y-4"
            >
              <div className="flex items-center mb-4">
                <FontAwesomeIcon icon={faChartLine} className="text-yellow-500 text-2xl mr-3" />
                <h3 className="text-lg font-medium">Buscar via yFinance</h3>
              </div>
              <p className="text-gray-600 mb-4">Busque ativos usando a API do yFinance.</p>

              <FormField
                control={yForm.control}
                name="ticker"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Código do Ativo</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input placeholder="Ex: PETR4, VALE3, BTC-USD" {...field} />
                        <Button type="button" variant="ghost" size="icon" className="absolute right-1 top-1">
                          <FontAwesomeIcon icon={faSearch} />
                        </Button>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={yForm.control}
                name="overwrite"
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-2">
                    <FormControl>
                      <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                    <FormLabel className="text-sm">Sobrescrever dados existentes</FormLabel>
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full">
                Buscar e Importar
              </Button>
            </form>
          </Form>
        </div>
      </div>
    </section>
  );
}
