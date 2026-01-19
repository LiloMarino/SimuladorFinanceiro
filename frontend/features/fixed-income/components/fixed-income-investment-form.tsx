import { Button } from "@/shared/components/ui/button";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import type { InvestmentFormSchema } from "../schemas/investment-form";
import type { UseFormReturn } from "react-hook-form";
import { toast } from "sonner";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { formatMoney } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";

interface FixedIncomeInvestmentFormProps {
  form: UseFormReturn<InvestmentFormSchema>;
  id: string | undefined;
  availableCash: number;
}

export function FixedIncomeInvestmentForm({ form, id, availableCash }: FixedIncomeInvestmentFormProps) {
  const buyMutation = useMutationApi<{ quantity: number }>(`/api/fixed-income/${id}/buy`, {
    onSuccess: () => {
      toast.success("Investido com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const onSubmit = async (values: InvestmentFormSchema) => {
    const quantity = Number(normalizeNumberString(values.amount));
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

              <div className="flex items-center gap-2">
                <FormControl className="flex-1">
                  <Input
                    inputMode="decimal"
                    placeholder="0,00"
                    {...field}
                    onChange={(e) => field.onChange(formatMoney(e.target.value))}
                  />
                </FormControl>

                <Button
                  type="button"
                  variant="gray"
                  className="shrink-0 px-3"
                  disabled={availableCash === 0}
                  onClick={() => {
                    const maxAmount = formatMoney(String(Math.round(availableCash * 100)));
                    form.setValue("amount", maxAmount);
                  }}
                >
                  MÁX
                </Button>
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
