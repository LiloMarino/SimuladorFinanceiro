import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileCsv, faCloudUploadAlt } from "@fortawesome/free-solid-svg-icons";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Button } from "@/shared/components/ui/button";

const csvSchema = z.object({
  ticker: z.string().min(1, "Informe o nome do ativo"),
  csv_file: z.any().refine((file) => file instanceof File, "Selecione um arquivo CSV válido"),
  overwrite: z.boolean(),
});

export type CsvFormData = z.infer<typeof csvSchema>;

interface CsvFormProps {
  onSubmit: (data: CsvFormData) => void;
}

export default function CSVForm({ onSubmit }: CsvFormProps) {
  const csvForm = useForm<CsvFormData>({
    resolver: zodResolver(csvSchema),
    defaultValues: { ticker: "", csv_file: undefined, overwrite: false },
  });

  return (
    <Form {...csvForm}>
      <form onSubmit={csvForm.handleSubmit(onSubmit)} className="border rounded-lg p-6 space-y-4">
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
                  className="border-2 border-dashed border-gray-300 rounded-md p-6 text-center cursor-pointer"
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
                  {field.value && <p className="mt-2 text-sm text-gray-700">{(field.value as File).name}</p>}
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

        <Button type="submit" variant="blue" className="w-full">
          Importar CSV
        </Button>
      </form>
    </Form>
  );
}
