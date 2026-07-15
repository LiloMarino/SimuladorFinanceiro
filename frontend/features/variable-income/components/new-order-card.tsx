import { Card } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormMessage, FormControl } from "@/shared/components/ui/form";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { displayMoney } from "@/shared/lib/utils/display";
import type { OrderAction, OrderType, Position } from "@/types";
import clsx from "clsx";
import { Minus, Plus, TrendingDown, TrendingUp } from "lucide-react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";
import { VariableIncomeStock } from "@/features/variable-income/models/VariableIncomeStock";

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
    },
  );

type NewOrderFormInput = z.input<typeof newOrderSchema>;
type NewOrderFormOutput = {
  action: OrderAction;
  type: OrderType;
  quantity: number;
  limit_price?: number;
};

interface NewOrderCardProps {
  stock: VariableIncomeStock;
  cash: number;
  position: Position | null;
}

export function NewOrderCard({ stock, cash, position }: NewOrderCardProps) {
  const form = useForm<NewOrderFormInput>({
    resolver: zodResolver(newOrderSchema),
    defaultValues: {
      action: "buy",
      type: "market",
      quantity: "",
      limit_price: "",
    },
  });

  const executeOrderMutation = useApiMutation({
    mutationFn: (payload: NewOrderFormOutput) =>
      apiFetch<{ order_id: string; status: string }>(`/api/variable-income/${stock.ticker}/orders`, {
        method: "POST",
        body: payload,
      }),
    onSuccess: (data) => {
      if (data.status === "PARTIAL") {
        toast.warning("Ordem executada parcialmente", {
          description: "Não foi possível completar a execução por falta de liquidez",
        });
      } else {
        toast.success("Ordem enviada com sucesso!");
      }
      form.reset();
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const type = form.watch("type");
  const action = form.watch("action");
  const quantity = Number(form.watch("quantity"));
  const limitPrice = Number(normalizeNumberString(form.watch("limit_price")));

  const marketEstimatedPrice = stock.getMarketPrice(action);
  const estimatedPrice = type === "market" ? marketEstimatedPrice : limitPrice;
  const estimatedTotal = estimatedPrice !== null ? quantity * estimatedPrice : null;

  // Quantidade em posição
  const positionSize = position?.size ?? 0;

  const onSubmit = async (values: NewOrderFormInput) => {
    const payload: NewOrderFormOutput = {
      action: values.action,
      type: values.type,
      quantity: Number(values.quantity),
      ...(values.type === "limit" && {
        limit_price: Number(normalizeNumberString(values.limit_price)),
      }),
    };

    await executeOrderMutation.mutateAsync(payload);
  };

  return (
    <Card className="flex-1 bg-muted/40 p-4 gap-4">
      <h3 className="font-medium">Nova Ordem</h3>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-4">
          {/* Operação */}
          <FormField
            control={form.control}
            name="action"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tipo de Operação</FormLabel>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    className={clsx(
                      "flex-1",
                      field.value === "buy" &&
                        "border-success bg-success/10 text-success hover:bg-success/20 hover:text-success",
                    )}
                    onClick={() => field.onChange("buy")}
                  >
                    <TrendingUp />
                    Compra
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    className={clsx(
                      "flex-1",
                      field.value === "sell" &&
                        "border-destructive bg-destructive/10 text-destructive hover:bg-destructive/20 hover:text-destructive",
                    )}
                    onClick={() => field.onChange("sell")}
                  >
                    <TrendingDown />
                    Venda
                  </Button>
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
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={field.value === "market" ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => field.onChange("market")}
                  >
                    À Mercado
                  </Button>
                  <Button
                    type="button"
                    variant={field.value === "limit" ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => field.onChange("limit")}
                  >
                    Limitada
                  </Button>
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
                <FormLabel>Quantidade</FormLabel>

                <div className="flex gap-2 items-center">
                  <FormControl className="flex-1">
                    <Input
                      {...field}
                      inputMode="numeric"
                      placeholder="Quantidade"
                      onChange={(e) => field.onChange(formatPositiveInteger(e.target.value))}
                    />
                  </FormControl>

                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      let maxQty = 0;
                      if (action === "buy") {
                        if (type === "market") {
                          // Ordem à mercado: cash / melhor preço atual do book
                          maxQty = marketEstimatedPrice ? Math.floor(cash / marketEstimatedPrice) : 0;
                        } else {
                          // Ordem limitada: cash / preço desejado
                          const price = limitPrice || stock.close;
                          maxQty = Math.floor(cash / price);
                        }
                      } else {
                        // Venda: só pode vender o que tem na posição
                        maxQty = positionSize;
                      }
                      form.setValue("quantity", String(maxQty));
                    }}
                    disabled={action === "buy" ? cash === 0 : positionSize === 0}
                    className="shrink-0 px-3"
                  >
                    Máx
                  </Button>
                </div>

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
            disabled={executeOrderMutation.isPending}
            variant={action === "buy" ? "default" : "destructive"}
          >
            {executeOrderMutation.isPending ? (
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
              <span className="font-semibold">
                {estimatedTotal !== null ? displayMoney(estimatedTotal) : "Indisponível"}
              </span>
            </div>

            {type === "limit" && (
              <p className="text-xs text-muted-foreground italic">
                * Ordem será executada quando o preço atingir {displayMoney(limitPrice)}
              </p>
            )}

            {type === "market" && (
              <p className="text-xs text-muted-foreground italic">
                {estimatedPrice === null
                  ? "* Sem preço disponível no book para estimar a ordem de mercado."
                  : "* O preço pode variar conforme o mercado."}
              </p>
            )}
          </div>
        </form>
      </Form>
    </Card>
  );
}
