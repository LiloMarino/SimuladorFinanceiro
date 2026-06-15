import { TrendingUp } from "lucide-react";
import { useForm } from "react-hook-form";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Button } from "@/shared/components/ui/button";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const yFinanceSchema = z.object({
  ticker: z.string().min(1, "Informe o código do ativo"),
  overwrite: z.boolean(),
});

export type YFinanceFormData = z.infer<typeof yFinanceSchema>;

interface YFinanceFormProps {
  onSubmit: (data: YFinanceFormData) => void;
}

export default function YFinanceForm({ onSubmit }: YFinanceFormProps) {
  const yForm = useForm<YFinanceFormData>({
    resolver: zodResolver(yFinanceSchema),
    defaultValues: { ticker: "", overwrite: false },
  });

  return (
    <Form {...yForm}>
      <form onSubmit={yForm.handleSubmit(onSubmit)} className="border rounded-lg p-6 space-y-4">
        <div className="flex items-center mb-4">
          <TrendingUp className="w-6 h-6 text-yellow-500 mr-3" />
          <h3 className="text-lg font-semibold">Buscar via yFinance</h3>
        </div>
        <p className="text-gray-600 mb-4">Busque ativos usando a API do yFinance.</p>

        <FormField
          control={yForm.control}
          name="ticker"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Código do Ativo</FormLabel>
              <FormControl>
                <Input placeholder="Ex: PETR4, VALE3, BTC-USD" {...field} />
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

        <Button type="submit" variant="default" className="w-full">
          Buscar e Importar
        </Button>
      </form>
    </Form>
  );
}
