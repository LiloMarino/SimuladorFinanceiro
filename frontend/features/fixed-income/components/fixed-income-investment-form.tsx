import { Button } from "@/shared/components/ui/button";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import type { InvestmentFormSchema } from "../schemas/investment-form";
import type { UseFormReturn } from "react-hook-form";
import { toast } from "sonner";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { formatMoney } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";
import { toCentsString } from "@/shared/lib/utils/display";

interface FixedIncomeInvestmentFormProps {
  form: UseFormReturn<InvestmentFormSchema>;
  id: string;
  availableCash: string;
}

export function FixedIncomeInvestmentForm({ form, id, availableCash }: FixedIncomeInvestmentFormProps) {
  const buyMutation = useApiMutation({
    mutationFn: (payload: { quantity: string }) => apiFetch(`/api/fixed-income/${id}/buy`, { method: "POST", body: payload }),
    onSuccess: () => {
      toast.success("Investido com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const onSubmit = async (values: InvestmentFormSchema) => {
    await buyMutation.mutateAsync({
      quantity: normalizeNumberString(values.amount),
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
                  variant="outline"
                  className="shrink-0 px-3"
                  disabled={Number(availableCash) === 0}
                  onClick={() => {
                    const maxAmount = formatMoney(toCentsString(availableCash));
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
          variant="default"
          disabled={buyMutation.isPending}
          className="w-full bg-success hover:bg-success/90 text-success-foreground py-6 text-base font-semibold rounded-lg"
        >
          {buyMutation.isPending ? "Investindo..." : "Investir agora"}
        </Button>
      </form>
    </Form>
  );
}
