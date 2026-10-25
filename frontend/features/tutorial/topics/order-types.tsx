import { AnimatePresence, motion } from "motion/react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { OrderBookCard } from "@/features/variable-income/components/order-book-card";
import { OrderTicket } from "@/features/variable-income/components/order-ticket";
import type { Order } from "@/types";
import type { IllustrationProps } from "../lib/topics";
import { STAGE_MY_LIMIT_ORDER, STAGE_SELL_BOOK } from "../stage/stage-data";
import { Cursor, Highlight, PressWhen, StageToast, StepMarker, TypeInto } from "../stage/stage-kit";
import { useAfter } from "../stage/useAfter";
import { buttonNamed, byId, tableRow, type Finder } from "../stage/targets";
import { TutorialStage } from "../stage/tutorial-stage";

// Trechos da linha do tempo (índices de `beats` em topics.ts)
const MARKET_TICKET = 0;
const MARKET_BOOK = 1;
const MARKET_FILLED = 2;
const LIMIT_TICKET = 3;
const LIMIT_PRICE = 4;
const WAITING = 5;
const LIMIT_FILLED = 6;
const COMPARE = 7;

const LIMIT_TEXT = "37,50";
const LIMIT_INPUT = byId("order-limit");

interface Target {
  id: string;
  finder: Finder;
  at?: readonly [number, number];
  click?: boolean;
  settle?: number;
}

/** O que o cursor, o contorno e o marcador apontam em cada trecho; a comparação final não tem alvo. */
const TARGETS: Record<number, Target> = {
  [MARKET_TICKET]: { id: "market", finder: buttonNamed("A mercado"), at: [0.5, 0.5], settle: 600 },
  [MARKET_BOOK]: { id: "best-sale", finder: tableRow("38,12"), at: [0.5, 0.5], settle: 700 },
  [MARKET_FILLED]: { id: "best-sale", finder: tableRow("38,12"), at: [0.5, 0.5] },
  [LIMIT_TICKET]: { id: "limit", finder: buttonNamed("Limitada"), click: true, settle: 700 },
  [LIMIT_PRICE]: { id: "limit-input", finder: LIMIT_INPUT, at: [0.3, 0.5], click: true },
  [WAITING]: { id: "mine", finder: tableRow("Lilo"), at: [0.3, 0.5], settle: 700 },
  [LIMIT_FILLED]: { id: "mine", finder: tableRow("Lilo"), at: [0.3, 0.5] },
};

const withBought = (orders: Order[]) =>
  orders.map((order, i) => (i === 0 ? { ...order, size: "400", remaining: "400" } : order));

const priceDrop: Order[] = [
  { ...STAGE_SELL_BOOK[0], id: "s4", size: "400", remaining: "400", limit_price: 37.9 },
  { ...STAGE_SELL_BOOK[0], id: "s5", size: "100", remaining: "100", limit_price: 37.5 },
];

export default function OrderTypesIllustration({ beat, step, still = false }: IllustrationProps) {
  const onTicket = beat === MARKET_TICKET || beat === LIMIT_TICKET || beat === LIMIT_PRICE;
  const onBook = beat >= MARKET_BOOK && beat <= LIMIT_FILLED && !onTicket;
  const matched = useAfter(LIMIT_FILLED, beat, 1100);
  const target = TARGETS[beat];

  const orders: Order[] =
    beat === MARKET_BOOK
      ? STAGE_SELL_BOOK
      : beat === MARKET_FILLED
        ? withBought(STAGE_SELL_BOOK)
        : beat === WAITING
          ? [...withBought(STAGE_SELL_BOOK), STAGE_MY_LIMIT_ORDER]
          : matched
            ? [priceDrop[0]]
            : [...priceDrop, STAGE_MY_LIMIT_ORDER];

  return (
    <TutorialStage width={720} height={700}>
      <div className="absolute inset-0 bg-background p-5">
        <AnimatePresence mode="wait">
          <motion.div
            key={onTicket ? "ticket" : onBook ? "book" : "compare"}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {onTicket && (
              <div className="mx-auto w-[420px]">
                <OrderTicket ticker="PETR4" assetClass="STOCK" todayPrice={38.12} />
              </div>
            )}
            {onBook && <OrderBookCard ticker="PETR4" orders={orders} />}
            {beat === COMPARE && <Comparison />}
          </motion.div>
        </AnimatePresence>

        {onTicket && <PressWhen finder={buttonNamed("Limitada")} id="kind" pressed={beat >= LIMIT_TICKET} delay={900} />}
        {onTicket && beat >= LIMIT_TICKET && (
          <TypeInto
            finder={LIMIT_INPUT}
            text={beat === LIMIT_PRICE || still ? LIMIT_TEXT : ""}
            typing={beat === LIMIT_PRICE}
            delay={1000}
            interval={150}
          />
        )}
        {beat === MARKET_FILLED && <StageToast>Executada · 100 × R$ 38,12</StageToast>}
        {matched && <StageToast>Executada · 100 × R$ 37,50</StageToast>}
        {beat === WAITING && <WaitingChip>Aguardando · 14 mar 2023</WaitingChip>}
        {beat === LIMIT_FILLED && <WaitingChip>17 mar 2023</WaitingChip>}

        {!still && target && (
          <>
            {(beat === LIMIT_PRICE || beat === WAITING) && (
              <Highlight finder={target.finder} id={target.id} settle={target.settle} />
            )}
            <StepMarker finder={target.finder} id={`${target.id}:${beat}`} step={step + 1} settle={target.settle} />
            <Cursor
              finder={target.finder}
              id={`${target.id}:${beat}`}
              at={target.at}
              click={target.click}
              settle={target.settle}
              start={{ x: 560, y: 40 }}
            />
          </>
        )}
      </div>
    </TutorialStage>
  );
}

function WaitingChip({ children }: { children: string }) {
  return (
    <Badge variant="warning" className="absolute bottom-4 left-5 z-30">
      {children}
    </Badge>
  );
}

/** As duas ordens lado a lado, com o que cada uma garante. */
function Comparison() {
  return (
    <div className="mx-auto grid max-w-[560px] grid-cols-2 gap-4 pt-24">
      <Card>
        <CardHeader>
          <CardTitle>A mercado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-1.5 text-[13px]">
            <span className="font-mono text-lg font-semibold">R$ 38,12</span>
            <span className="text-success">Compra na hora</span>
            <span className="text-muted-foreground">O preço pode variar</span>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Limitada</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-1.5 text-[13px]">
            <span className="font-mono text-lg font-semibold">R$ 37,50</span>
            <span className="text-destructive">Pode não executar</span>
            <span className="text-muted-foreground">O preço é o que você pediu</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
