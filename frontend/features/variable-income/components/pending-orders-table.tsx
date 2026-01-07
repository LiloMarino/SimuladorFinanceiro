import clsx from "clsx";
import { Card } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Badge } from "@/shared/components/ui/badge";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { Order } from "@/types";
import { FileText, XCircle } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";

interface PendingOrdersCardProps {
  ticker: string;
}

export function PendingOrdersCard({ ticker }: PendingOrdersCardProps) {
  const { data: pendingOrders, setData: setPendingOrders } = useQueryApi<Order[]>(
    `/api/variable-income/${ticker}/orders`
  );

  useRealtime(`order_added:${ticker}`, ({ order }) => {
    setPendingOrders((prev) => {
      if (!prev) return [order];

      if (prev.some((o) => o.id === order.id)) {
        return prev;
      }

      return [...prev, order];
    });
  });

  useRealtime(`order_updated:${ticker}`, ({ order }) => {
    setPendingOrders((prev) => {
      if (!prev) return prev;
      return prev.map((o) => (o.id === order.id ? order : o));
    });
  });

  const cancelOrderMutation = useMutationApi(`/api/variable-income/${ticker}/orders`, {
    method: "DELETE",
    onSuccess: () => {
      toast.info("Ordem cancelada com sucesso!");
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const handleCancelOrder = async (orderId: string) => {
    await cancelOrderMutation.mutate({ order_id: orderId });
  };

  if (!pendingOrders || pendingOrders.length === 0) {
    return (
      <Card className="p-4 bg-background border">
        <h3 className="font-medium mb-4">Ordens Pendentes</h3>

        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-3 mb-3">
            <FileText className="h-6 w-6 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium">Nenhuma ordem pendente</p>
          <p className="text-sm text-muted-foreground mt-1">Suas ordens aparecerão aqui quando forem criadas.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 bg-background border">
      <TooltipProvider>
        <h3 className="font-medium mb-4">Ordens Pendentes</h3>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data</TableHead>
                <TableHead>Usuário</TableHead>
                <TableHead>Tipo da Operação</TableHead>
                <TableHead>Quantidade</TableHead>
                <TableHead>Preço</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ação</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {pendingOrders.map((order) => {
                const canCancel = order.status === "pending";
                return (
                  <TableRow key={order.id}>
                    <TableCell>
                      {new Date(order.created_at).toLocaleDateString("pt-BR", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </TableCell>

                    <TableCell className="text-muted-foreground">{order.player_nickname}</TableCell>

                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={order.action === "buy" ? "default" : "destructive"}
                          className={clsx(
                            order.action === "buy"
                              ? "bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400"
                              : "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400"
                          )}
                        >
                          {order.action === "buy" ? "Compra" : "Venda"}
                        </Badge>
                      </div>
                    </TableCell>

                    <TableCell className="font-medium">
                      {order.status === "partial" ? (
                        <div className="flex flex-col leading-tight">
                          <span>
                            {order.size - order.remaining} / {order.size}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {displayPercent((order.size - order.remaining) / order.size, 0)} executada
                          </span>
                        </div>
                      ) : (
                        order.size
                      )}
                    </TableCell>

                    <TableCell className="font-medium">{displayMoney(order.limit_price ?? 0)}</TableCell>

                    <TableCell>
                      <Badge
                        variant="outline"
                        className={clsx(
                          order.status === "executed" &&
                            "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",

                          order.status === "partial" &&
                            "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",

                          order.status === "pending" && "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",

                          order.status === "canceled" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                        )}
                      >
                        {order.status === "executed" && "Efetivada"}
                        {order.status === "partial" && "Parcialmente executada"}
                        {order.status === "pending" && "Pendente"}
                        {order.status === "canceled" && "Cancelada"}
                      </Badge>
                    </TableCell>

                    <TableCell>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button
                            onClick={() => handleCancelOrder(order.id)}
                            disabled={!canCancel || cancelOrderMutation.loading}
                            className={clsx(
                              "p-1 rounded transition-colors",
                              canCancel
                                ? "text-red-600 hover:bg-red-100 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-900/30"
                                : "text-muted-foreground cursor-not-allowed"
                            )}
                          >
                            <XCircle className="h-4 w-4" />
                          </button>
                        </TooltipTrigger>

                        <TooltipContent side="top">
                          {canCancel ? "Cancelar ordem" : "Não é possível cancelar ordens não pendentes"}
                        </TooltipContent>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </TooltipProvider>
    </Card>
  );
}
