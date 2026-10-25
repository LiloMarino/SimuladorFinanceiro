import { displayDayMonth, displayList } from "@/shared/lib/utils/display";
import type { GovernmentNotice } from "@/types";
import { lowStreakLabel } from "./government";

export type MeasureToast = {
  tone: "success" | "info" | "warning" | "error";
  title: string;
  description: string;
};

/** Os ativos da medida que o jogador tem, para o aviso falar da carteira dele. */
function heldTickers(event: GovernmentNotice, held: string[]) {
  return (event.tickers ?? []).filter((ticker) => held.includes(ticker));
}

/** O Congresso votou: o que muda, quando vale e, se o jogador tem os ativos, o que isso diz da carteira dele. */
export function votedToast(event: GovernmentNotice, held: string[]): MeasureToast {
  const title = event.measure_title ?? "medida";
  if (!event.accepted) {
    return {
      tone: "warning",
      title: `Congresso rejeitou: ${title}`,
      description: `Tinha ${event.chance}% de chance. Nada muda.`,
    };
  }
  const mine = heldTickers(event, held);
  const when = event.effective ? `Vale em ${displayDayMonth(event.effective)}, daqui a 90 dias.` : "";
  const wallet =
    mine.length > 0 ? ` Você tem ${displayList(mine)}: a regra vale para as vendas com lucro depois disso.` : "";
  return { tone: "success", title: `Congresso aprovou: ${title}`, description: `${when}${wallet}`.trim() };
}

/** A medida passou a valer hoje: sobre quais ativos, quando é setorial. */
export function inForceToast(event: GovernmentNotice): MeasureToast {
  const tickers = event.tickers ?? [];
  const shown = tickers.slice(0, 2);
  const rest = tickers.length - shown.length;
  const scope =
    tickers.length === 0
      ? "Vale para todos os jogadores."
      : `Vale para todas as vendas com lucro de ${rest > 0 ? `${shown.join(", ")} e mais ${rest} ${rest === 1 ? "ativo" : "ativos"}` : displayList(shown)}.`;
  return {
    tone: "info",
    title: `Valendo a partir de hoje: ${event.measure_title ?? "medida"}`,
    description: scope,
  };
}

/** Aviso ao presidente de que um mês abaixo do piso separa o governo do impeachment. */
export function warningToast(event: GovernmentNotice, floor: number): MeasureToast {
  const months = event.months_below_floor ?? 0;
  return {
    tone: "error",
    title: lowStreakLabel({ low_streak: months, floor }),
    description: `Aprovação de ${event.approval ?? "?"}% no fechamento do mês. Mais um mês abaixo do piso e o impeachment tira você do governo.`,
  };
}
