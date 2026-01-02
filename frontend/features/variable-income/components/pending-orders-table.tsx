import clsx from "clsx";
import { Card } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Badge } from "@/shared/components/ui/badge";
import { displayMoney } from "@/shared/lib/utils/display";
import type { PendingOrder } from "@/types";
import { FileText } from "lucide-react";

interface PendingOrdersCardProps {
  pendingOrders?: PendingOrder[] | null;
  onCancelOrder: (orderId: string) => void;
  cancelLoading?: boolean;
}

export function PendingOrdersCard({ pendingOrders, onCancelOrder, cancelLoading = false }: PendingOrdersCardProps) {
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
      <h3 className="font-medium mb-4">Ordens Pendentes</h3>

      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Tipo da Operação</TableHead>
              <TableHead>Quantidade</TableHead>
              <TableHead>Preço</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Usuário</TableHead>
              <TableHead>Ação</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {pendingOrders.map((order) => (
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

                <TableCell>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={order.operation === "buy" ? "default" : "destructive"}
                      className={clsx(
                        order.operation === "buy"
                          ? "bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400"
                      )}
                    >
                      {order.operation === "buy" ? "Compra" : "Venda"}
                    </Badge>
                    <Badge variant="outline" className="bg-background">
                      {order.type === "market" ? "Mercado" : "Limitada"}
                    </Badge>
                  </div>
                </TableCell>

                <TableCell className="font-medium">{order.quantity}</TableCell>

                <TableCell className="font-medium">
                  {order.type === "limit" && order.limit_price ? displayMoney(order.limit_price) : "Mercado"}
                </TableCell>

                <TableCell>
                  <Badge
                    variant="outline"
                    className={clsx(
                      order.status === "filled" && "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
                      order.status === "partial" &&
                        "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
                      order.status === "pending" && "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
                    )}
                  >
                    {order.status === "filled" && "Efetivada"}
                    {order.status === "partial" && "Parcial"}
                    {order.status === "pending" && "Pendente"}
                  </Badge>
                </TableCell>

                <TableCell className="text-muted-foreground">{order.user_name}</TableCell>

                <TableCell>
                  {order.status !== "filled" && (
                    <button
                      onClick={() => onCancelOrder(order.id)}
                      disabled={cancelLoading}
                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium disabled:opacity-50 transition-colors"
                    >
                      Cancelar
                    </button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}
