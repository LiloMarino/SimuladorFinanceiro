import { AnimatePresence, motion } from "motion/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { MarketTable } from "@/features/variable-income/components/market-table";
import { OrderTicket } from "@/features/variable-income/components/order-ticket";
import { PositionCard } from "@/features/variable-income/components/position-card";
import { StockHeader } from "@/features/variable-income/components/stock-header";
import type { IllustrationProps } from "../lib/topics";
import { STAGE_POSITION, STAGE_QUOTES, STAGE_STOCK } from "../stage/stage-data";
import { Cursor, Highlight, StageToast, StepMarker, TypeInto } from "../stage/stage-kit";
import {
  bySelector,
  buttonNamed,
  byId,
  lastButtonStartingWith,
  tableHeader,
  tableRow,
  withText,
  type Finder,
} from "../stage/targets";
import { TutorialStage } from "../stage/tutorial-stage";

// Trechos da linha do tempo (índices de `beats` em topics.ts)
const LIST = 0;
const ROW = 1;
const DETAIL = 2;
const TICKET = 3;
const FOCUS = 4;
const TYPING = 5;
const CONFIRM = 6;
const BOUGHT = 7;
const PORTFOLIO = 8;

const NO_HOLDINGS = new Map<string, string>();
const SIZE = byId("order-size");

interface Target {
  id: string;
  finder: Finder;
  at?: readonly [number, number] | undefined;
  click?: boolean | undefined;
  /** Espera até o alvo terminar de entrar em cena. */
  settle?: number | undefined;
}

/** O que o cursor, o contorno e o marcador apontam em cada trecho. */
const TARGETS: Record<number, Target> = {
  [LIST]: { id: "list", finder: tableHeader("Ativo"), at: [0.3, 0.5] },
  [ROW]: { id: "row", finder: tableRow("PETR4"), at: [0.2, 0.5] },
  [DETAIL]: { id: "price", finder: withText("span", "R$ 38,12"), at: [0.5, 0.5] },
  [TICKET]: { id: "buy", finder: buttonNamed("Comprar"), click: true, settle: 800 },
  [FOCUS]: { id: "size", finder: SIZE, at: [0.3, 0.5], click: true },
  [TYPING]: { id: "size", finder: SIZE, at: [0.3, 0.5] },
  [CONFIRM]: { id: "submit", finder: lastButtonStartingWith("Comprar "), click: true },
  [BOUGHT]: { id: "submit", finder: lastButtonStartingWith("Comprar ") },
  [PORTFOLIO]: { id: "position", finder: bySelector("[data-slot=card]") },
};

const SIZE_TEXT = "100";

export default function BuyStockIllustration({ beat, step, still = false }: IllustrationProps) {
  const screen = beat <= ROW ? "list" : beat < PORTFOLIO ? "detail" : "portfolio";
  const ticketOnStage = beat >= TICKET && beat < PORTFOLIO;
  const target = TARGETS[beat];

  return (
    <TutorialStage width={720} height={720}>
      <div className="absolute inset-0 bg-background p-5">
        <AnimatePresence mode="wait">
          <motion.div
            key={screen}
            className="grid content-start gap-4"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {screen === "list" && (
              <Card size="flush">
                <MarketTable quotes={STAGE_QUOTES} holdings={NO_HOLDINGS} message={null} />
              </Card>
            )}
            {screen === "detail" && (
              <>
                <StockHeader stock={STAGE_STOCK} />
                {ticketOnStage && (
                  <motion.div
                    className="mx-auto w-[420px]"
                    initial={{ opacity: 0, y: 48 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <OrderTicket ticker="PETR4" assetClass="STOCK" todayPrice={38.12} />
                  </motion.div>
                )}
              </>
            )}
            {screen === "portfolio" && (
              <div className="mx-auto grid w-[420px] gap-4">
                <PositionCard ticker="PETR4" position={STAGE_POSITION} />
                <Card>
                  <CardHeader>
                    <CardTitle>Caixa</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-mono text-lg font-semibold">R$ 96.188,00</p>
                  </CardContent>
                </Card>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {ticketOnStage && (
          <TypeInto finder={SIZE} text={beat >= TYPING ? SIZE_TEXT : ""} typing={beat === TYPING} delay={600} />
        )}
        {beat === BOUGHT && <StageToast>Compra de 100 PETR4 feita</StageToast>}

        {!still && target && (
          <>
            {(beat === ROW || beat === FOCUS || beat === TYPING || beat === PORTFOLIO) && (
              <Highlight finder={target.finder} id={target.id} settle={target.settle} />
            )}
            <StepMarker finder={target.finder} id={`${target.id}:${beat}`} step={step + 1} settle={target.settle} />
            {beat !== PORTFOLIO && (
              <Cursor
                finder={target.finder}
                id={`${target.id}:${beat}`}
                at={target.at}
                click={target.click}
                settle={target.settle}
                start={{ x: 560, y: 40 }}
              />
            )}
          </>
        )}
      </div>
    </TutorialStage>
  );
}
