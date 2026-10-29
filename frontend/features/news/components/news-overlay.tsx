import { cn } from "@/shared/lib/utils";
import { useNewsPresenter } from "../hooks/useNewsPresenter";
import { NewsCard } from "./news-card";
import { NewsSeal } from "./news-seal";
import { NewsWindow } from "./news-window";

// O canto do cartão e do selo; a esquerda começa depois do menu lateral
const CORNER = {
  BOTTOM_LEFT: "bottom-6 left-[calc(var(--sidebar-width)+1.5rem)]",
  BOTTOM_RIGHT: "right-6 bottom-6",
  TOP_LEFT: "top-24 left-[calc(var(--sidebar-width)+1.5rem)]",
} as const;

/**
 * A janela no centro e o cartão (ou o selo) no canto escolhido. Na faixa, o cartão não existe:
 * a manchete mora na linha sob a topbar.
 */
export function NewsOverlay() {
  const { state, position, closeWindow } = useNewsPresenter();
  const { lead, window } = state;
  const corner = position === undefined || position === "STRIP" ? null : CORNER[position];

  return (
    <>
      {window && (
        <div className="fixed top-1/2 left-1/2 z-50 -translate-x-1/2 -translate-y-[56%] rounded-xl shadow-[0_24px_64px_rgba(15,23,41,.28)]">
          <NewsWindow key={window.id} news={window} onClose={closeWindow} />
        </div>
      )}
      {corner && lead && (
        <div className={cn("fixed z-40", corner)}>
          {state.expanded ? (
            <div className="rounded-xl shadow-[0_12px_32px_rgba(15,23,41,.18)]">
              <NewsCard news={lead.news} others={state.count - 1} />
            </div>
          ) : (
            <NewsSeal date={lead.news.news_date} />
          )}
        </div>
      )}
    </>
  );
}
