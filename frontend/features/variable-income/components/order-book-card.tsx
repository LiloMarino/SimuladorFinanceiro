import { useState } from "react";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { InfoHint } from "@/shared/components/info-hint";
import { useAuth } from "@/shared/hooks/useAuth";
import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import type ApiError from "@/shared/lib/models/ApiError";
import { displayMoney } from "@/shared/lib/utils/display";
import type { Order } from "@/types";
import { useCancelOrder } from "../hooks/mutations/useCancelOrder";
import { bookSpread, isOpenOrder, splitBook } from "../lib/order-book";
import { MyOrdersStrip } from "./my-orders-strip";
import { OrderBookColumns, OrderBookColumnsSkeleton } from "./order-book-columns";
import { OrderBookSpread, OrderBookSpreadSkeleton } from "./order-book-spread";
import { TradeHistory } from "./trade-history";

type Tab = "OPEN" | "HISTORY";

type OrderBookCardProps = {
  ticker: string;
  orders: Order[];
  /** Preço típico de hoje: o centro das ofertas do Mercado */
  typicalPrice: number;
  isLoading?: boolean;
  error?: ApiError | null | undefined;
  onRetry?: () => void;
  /** Clique numa oferta de outro jogador: a boleta prepara a ordem do outro lado */
  onPick: (order: Order) => void;
};

function OrderBookHint() {
  return (
    <InfoHint interactive label="De onde vêm essas ofertas">
      <div className="grid gap-2 text-[13px] leading-normal">
        <p className="font-semibold">De onde vêm essas ofertas</p>
        <p>
          O Mercado coloca ofertas dos dois lados do <b>preço típico</b> de hoje, a média da máxima, da mínima e do
          fechamento: (12,67 + 12,13 + 12,20) ÷ 3 = <b>R$ 12,33</b>. Compras ficam abaixo, vendas acima. Os jogadores e
          os robôs da sala entram na mesma fila.
        </p>
        <p>
          <b>Exemplo:</b> uma compra limitada a R$ 12,35 encontra a venda de R$ 12,35 e executa no próximo pregão. A R$
          11,59 ela espera alguém vender tão barato, e pode não executar.
        </p>
        <p>
          <b>Diferença</b> é a distância entre a melhor venda e a melhor compra: R$ 12,35 − R$ 12,33 = R$ 0,02 (0,16% do
          preço). Abaixo de 0,5% é barato entrar e sair; acima de 2%, comprar e vender na hora já custa caro.
        </p>
        <p>
          <b>Barra</b> é a quantidade da linha comparada com a maior do livro.
        </p>
      </div>
    </InfoHint>
  );
}

/** Livro de ofertas do ativo: as ordens abertas da sala em duas colunas e o histórico de negócios. */
export function OrderBookCard({
  ticker,
  orders,
  typicalPrice,
  isLoading = false,
  error,
  onRetry,
  onPick,
}: OrderBookCardProps) {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("OPEN");
  const [expanded, setExpanded] = useState(false);

  const cancel = useCancelOrder(ticker);
  // Com o automático ligado as ordens abertas são da estratégia: só ela cancela
  const automatic = !!useMyStrategy().data?.active;

  const open = orders.filter(isOpenOrder);
  const book = splitBook(orders);
  const mine = open.filter((order) => !order.synthetic && order.player_nickname === user?.nickname);
  const loadFailed = !!error && open.length === 0;

  const body = () => {
    if (isLoading) {
      return (
        <>
          <OrderBookSpreadSkeleton />
          <OrderBookColumnsSkeleton />
        </>
      );
    }
    if (loadFailed) {
      return (
        <ErrorState
          title="Não deu para carregar o livro."
          description="As suas ordens continuam valendo; só a lista não chegou."
          error={error}
          onRetry={onRetry}
        />
      );
    }
    if (open.length === 0) {
      return (
        <Empty>
          <EmptyHeader>
            <EmptyTitle>Sem ofertas hoje</EmptyTitle>
            <EmptyDescription>
              Quando o Mercado ou alguém da sala puser uma oferta neste ativo, ela aparece aqui.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      );
    }
    return (
      <>
        <MyOrdersStrip
          orders={mine}
          bestBuy={book.buys[0]?.limit_price}
          automatic={automatic}
          cancelling={cancel.isPending}
          onCancel={(order) => cancel.mutate(order.id)}
        />
        <OrderBookSpread book={book} spread={bookSpread(book, typicalPrice)} />
        <OrderBookColumns
          book={book}
          nickname={user?.nickname}
          pickable={!automatic}
          expanded={expanded}
          onToggle={() => setExpanded((value) => !value)}
          onPick={onPick}
        />
      </>
    );
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <div className="flex items-center gap-1.5">
          <CardTitle>Livro de ofertas</CardTitle>
          <OrderBookHint />
        </div>
        {isLoading ? (
          <Skeleton className="h-3 w-[70%]" />
        ) : (
          <CardDescription>
            Ofertas de hoje em torno de <b className="font-mono text-foreground">{displayMoney(typicalPrice)}</b>. Sua
            ordem executa no próximo pregão se alguém aceitar o seu preço.
          </CardDescription>
        )}
        <CardAction>
          {isLoading ? (
            <Skeleton className="h-8 w-[170px]" />
          ) : (
            <ToggleGroup
              variant="segmented"
              aria-label="Ofertas ou histórico"
              value={[tab]}
              onValueChange={(values) => values[0] && setTab(values[0] as Tab)}
            >
              <ToggleGroupItem value="OPEN">Ofertas · {open.length}</ToggleGroupItem>
              <ToggleGroupItem value="HISTORY">Histórico</ToggleGroupItem>
            </ToggleGroup>
          )}
        </CardAction>
      </CardHeader>

      {tab === "OPEN" ? body() : <TradeHistory ticker={ticker} />}
    </Card>
  );
}
