import { Card } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormMessage, FormControl } from "@/shared/components/ui/form";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { displayMoney } from "@/shared/lib/utils/display";
import type { OrderAction, OrderType, StockDetails } from "@/types";
import clsx from "clsx";
import { Minus, Plus } from "lucide-react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";

const newOrderSchema = z
  .object({
    action: z.enum(["buy", "sell"]),
    type: z.enum(["market", "limit"]),
    quantity: z
      .string()
      .min(1, "Informe a quantidade")
      .refine((val) => Number(val) > 0, "Quantidade deve ser maior que zero"),
    limit_price: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.type === "limit") {
        return !!data.limit_price && Number(normalizeNumberString(data.limit_price)) > 0;
      }
      return true;
    },
    {
      path: ["limit_price"],
      message: "Informe um preço válido para ordem limitada",
    }
  );

type NewOrderFormInput = z.input<typeof newOrderSchema>;
type NewOrderFormOutput = {
  action: OrderAction;
  type: OrderType;
  quantity: number;
  limit_price?: number;
};

interface NewOrderCardProps {
  stock: StockDetails;
}

export function NewOrderCard({ stock }: NewOrderCardProps) {
  const form = useForm<NewOrderFormInput>({
    resolver: zodResolver(newOrderSchema),
    defaultValues: {
      action: "buy",
      type: "market",
      quantity: "",
      limit_price: "",
    },
  });

  const executeOrderMutation = useMutationApi(`/api/variable-income/${stock.ticker}/orders`, {
    onSuccess: () => {
      toast.success("Ordem enviada com sucesso!");
      form.reset();
    },
    onError: (err) => {
      toast.error(`Erro ao enviar ordem: ${err.message}`);
    },
  });

  const type = form.watch("type");
  const quantity = Number(form.watch("quantity"));
  const limitPrice = Number(normalizeNumberString(form.watch("limit_price")));

  const estimatedPrice = type === "market" ? stock.close : limitPrice;
  const estimatedTotal = quantity * estimatedPrice;

  const onSubmit = async (values: NewOrderFormInput) => {
    const payload: NewOrderFormOutput = {
      action: values.action,
      type: values.type,
      quantity: Number(values.quantity),
      ...(values.type === "limit" && {
        limit_price: Number(normalizeNumberString(values.limit_price)),
      }),
    };

    await executeOrderMutation.mutate(payload);
  };

  return (
    <Card className="flex-1 bg-muted/40 p-4">
      <h3 className="font-medium mb-4">Nova Ordem</h3>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-4">
          {/* Operação */}
          <FormField
            control={form.control}
            name="action"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tipo de Operação</FormLabel>
                <div className="flex gap-4">
                  {["buy", "sell"].map((op) => (
                    <label key={op} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={field.value === op}
                        onChange={() => field.onChange(op)}
                        className={clsx("w-4 h-4", op === "buy" ? "accent-green-600" : "accent-red-600")}
                      />
                      <span className="text-sm">{op === "buy" ? "Compra" : "Venda"}</span>
                    </label>
                  ))}
                </div>
              </FormItem>
            )}
          />

          {/* Tipo de Ordem */}
          <FormField
            control={form.control}
            name="type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tipo de Ordem</FormLabel>
                <div className="flex gap-4">
                  {["market", "limit"].map((t) => (
                    <label key={t} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={field.value === t}
                        onChange={() => field.onChange(t)}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">{t === "market" ? "À Mercado" : "Limitada"}</span>
                    </label>
                  ))}
                </div>
              </FormItem>
            )}
          />

          {/* Quantidade */}
          <FormField
            control={form.control}
            name="quantity"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input
                    {...field}
                    inputMode="numeric"
                    placeholder="Quantidade"
                    onChange={(e) => field.onChange(formatPositiveInteger(e.target.value))}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Preço Limitado */}
          {type === "limit" && (
            <FormField
              control={form.control}
              name="limit_price"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input
                      {...field}
                      inputMode="decimal"
                      placeholder="Preço desejado (R$)"
                      onChange={(e) => field.onChange(formatMoney(e.target.value))}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}

          {/* Botão */}
          <Button
            type="submit"
            disabled={executeOrderMutation.loading}
            className={clsx(
              form.watch("action") === "buy" ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"
            )}
          >
            {executeOrderMutation.loading ? (
              <Spinner className="h-4 w-4" />
            ) : (
              <>
                {form.watch("action") === "buy" ? <Plus className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                Executar {form.watch("action") === "buy" ? "Compra" : "Venda"}
              </>
            )}
          </Button>

          {/* Total estimado */}
          <div className="border-t pt-3 text-sm space-y-1">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total estimado:</span>
              <span className="font-semibold">{displayMoney(estimatedTotal)}</span>
            </div>

            {type === "limit" && (
              <p className="text-xs text-muted-foreground italic">
                * Ordem será executada quando o preço atingir {displayMoney(limitPrice)}
              </p>
            )}

            {type === "market" && (
              <p className="text-xs text-muted-foreground italic">* O preço pode variar conforme o mercado.</p>
            )}
          </div>
        </form>
      </Form>
    </Card>
  );
}
