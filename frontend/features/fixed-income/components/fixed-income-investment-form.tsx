import { Button } from "@/shared/components/ui/button";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import type { InvestmentFormSchema } from "../schemas/investment-form";
import type { UseFormReturn } from "react-hook-form";
import { toast } from "sonner";
import { useMutationApi } from "@/shared/hooks/useMutationApi";

interface FixedIncomeInvestmentFormProps {
  form: UseFormReturn<InvestmentFormSchema>;
  id: string | undefined;
}

export function FixedIncomeInvestmentForm({ form, id }: FixedIncomeInvestmentFormProps) {
  const buyMutation = useMutationApi<{ quantity: number }>(`/api/fixed-income/${id}/buy`, {
    onSuccess: () => {
      toast.success("Investido com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const onSubmit = async (values: InvestmentFormSchema) => {
    const quantity = Number(values.amount);

    await buyMutation.mutate({
      quantity,
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="amount"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Valor do investimento</FormLabel>
              <div className="relative ">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600 font-medium">R$</span>

                <FormControl>
                  <Input type="number" min="0" step="100" className="pl-10" placeholder="0,00" {...field} />
                </FormControl>
              </div>

              <FormMessage />
            </FormItem>
          )}
        />

        <Button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 text-white py-6 text-base font-semibold rounded-lg"
        >
          Investir agora
        </Button>
      </form>
    </Form>
  );
}
