import { Card } from "@/shared/components/ui/card";
import { Spinner } from "@/shared/components/ui/spinner";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { formatMoney } from "@/shared/lib/utils/formatting";
import type { StockDetails } from "@/types";
import clsx from "clsx";
import { Minus, Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function NewOrderCard({
  stock,
  refetchOrders,
  shouldRefreshPosition,
}: {
  stock: StockDetails;
  refetchOrders: () => void;
  shouldRefreshPosition: React.RefObject<boolean>;
}) {
  const [operationType, setOperationType] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [limitPrice, setLimitPrice] = useState<number>(0);
  const [quantity, setQuantity] = useState<number>(0);

  const executeOrderMutation = useMutationApi(`/api/variable-income/${stock.ticker}/order`, {
    onSuccess: () => {
      toast.success("Ordem enviada com sucesso!");
      setQuantity(0);
      setLimitPrice(0);
      shouldRefreshPosition.current = true;
      refetchOrders();
    },
    onError: (err) => {
      toast.error(`Erro ao enviar ordem: ${err.message}`);
    },
  });

  const handleExecuteOrder = async () => {
    if (!quantity || quantity <= 0) {
      toast.warning("Informe uma quantidade válida.");
      return;
    }

    if (orderType === "limit" && (!limitPrice || limitPrice <= 0)) {
      toast.warning("Informe um preço válido para ordem limitada.");
      return;
    }

    await executeOrderMutation.mutate({
      operation: operationType,
      type: orderType,
      quantity,
      ...(orderType === "limit" && { limit_price: limitPrice }),
    });
  };

  const estimatedPrice = orderType === "market" ? stock.close : limitPrice;
  const estimatedTotal = quantity * estimatedPrice;

  return (
    <Card className="flex-1 bg-muted/40 p-4">
      <h3 className="font-medium">Nova Ordem</h3>
      <div className="flex flex-col gap-4">
        {/* Tipo de Operação */}
        <div>
          <label className="text-sm font-medium mb-2 block">Tipo de Operação</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="operation"
                value="buy"
                checked={operationType === "buy"}
                onChange={(e) => setOperationType(e.target.value as "buy")}
                className="w-4 h-4 text-green-600 accent-green-600"
              />
              <span className="text-sm">Compra</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="operation"
                value="sell"
                checked={operationType === "sell"}
                onChange={(e) => setOperationType(e.target.value as "sell")}
                className="w-4 h-4 text-red-600 accent-red-600"
              />
              <span className="text-sm">Venda</span>
            </label>
          </div>
        </div>

        {/* Tipo de Ordem */}
        <div>
          <label className="text-sm font-medium mb-2 block">Tipo de Ordem</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="orderType"
                value="market"
                checked={orderType === "market"}
                onChange={(e) => setOrderType(e.target.value as "market")}
                className="w-4 h-4"
              />
              <span className="text-sm">À Mercado</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="orderType"
                value="limit"
                checked={orderType === "limit"}
                onChange={(e) => setOrderType(e.target.value as "limit")}
                className="w-4 h-4"
              />
              <span className="text-sm">Limitada</span>
            </label>
          </div>
        </div>

        {/* Inputs */}
        <div className="flex flex-col gap-2">
          <input
            type="number"
            placeholder="Quantidade"
            value={quantity || ""}
            min={0}
            onChange={(e) => {
              const value = e.target.value === "" ? 0 : Number(e.target.value);
              setQuantity(value >= 0 ? value : 0);
            }}
            className="flex-1 p-2 border rounded-md bg-background"
          />

          {/* Campo condicional para preço limitado */}
          {orderType === "limit" && (
            <input
              type="number"
              placeholder="Preço desejado (R$)"
              value={limitPrice || ""}
              min={0}
              step={0.01}
              onChange={(e) => {
                const value = e.target.value === "" ? 0 : Number(e.target.value);
                setLimitPrice(value >= 0 ? value : 0);
              }}
              className="flex-1 p-2 border rounded-md bg-background"
            />
          )}

          {/* Botão único para executar */}
          <button
            className={clsx(
              "py-2 px-4 rounded-md font-medium text-white flex items-center justify-center gap-2 transition-colors",
              operationType === "buy" ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700",
              executeOrderMutation.loading && "opacity-70 cursor-not-allowed"
            )}
            onClick={handleExecuteOrder}
            disabled={executeOrderMutation.loading}
          >
            {executeOrderMutation.loading ? (
              <Spinner className="h-4 w-4 text-white" />
            ) : (
              <>
                {operationType === "buy" ? <Plus className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                Executar {operationType === "buy" ? "Compra" : "Venda"}
              </>
            )}
          </button>
        </div>

        {/* Total estimado */}
        <div className="flex flex-col gap-1 border-t pt-3 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Total estimado:</span>
            <span className="font-semibold">{formatMoney(estimatedTotal)}</span>
          </div>
          {orderType === "limit" && (
            <p className="text-xs text-muted-foreground italic">
              * Ordem será executada quando o preço atingir R$ {limitPrice.toFixed(2)}
            </p>
          )}
          {orderType === "market" && (
            <p className="text-xs text-muted-foreground italic">
              * O preço pode variar conforme atualização do mercado.
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}
