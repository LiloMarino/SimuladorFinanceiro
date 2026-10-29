import { Link } from "react-router-dom";
import { Clock, X } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import type { News } from "@/types";
import { WINDOW_MS } from "../lib/presenter";
import { NewsKicker, NewsMasthead } from "./news-parts";

type NewsWindowProps = {
  news: News;
  onClose: () => void;
};

/**
 * A edição extra: a manchete no centro da tela, sem escurecer o fundo e sem pausar a partida.
 * A barra esvazia durante os WINDOW_MS em que ela fica aberta.
 */
export function NewsWindow({ news, onClose }: NewsWindowProps) {
  return (
    <Card
      variant="paper"
      size="flush"
      role="dialog"
      aria-label="Edição extra do jornal"
      className="w-[560px] max-w-[calc(100vw-2rem)]"
    >
      <NewsMasthead date={news.news_date}>
        <span className="flex items-center gap-2">
          <Badge variant="destructive" size="tag">
            EDIÇÃO EXTRA
          </Badge>
          <Button variant="ghost" size="icon-xs" aria-label="Fechar" onClick={onClose}>
            <X />
          </Button>
        </span>
      </NewsMasthead>
      <div className="grid gap-2 px-5.5 pt-4.5 pb-1.5">
        <NewsKicker type={news.news_type} />
        <p className="font-serif text-2xl leading-tight font-semibold">{news.headline}</p>
        {news.dek && <p className="text-sm text-muted-foreground">{news.dek}</p>}
      </div>
      <div className="flex items-center gap-2.5 px-5.5 pt-3.5 pb-4">
        <div className="grid flex-1 gap-1">
          <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="size-3.5" />O tempo continua correndo · fecha sozinha em {WINDOW_MS / 1000} s
          </span>
          <span className="h-1.5 w-56 overflow-hidden rounded-full bg-muted">
            <span
              className="block h-full origin-left animate-countdown rounded-full bg-faint-foreground"
              style={{ animationDuration: `${WINDOW_MS}ms` }}
            />
          </span>
        </div>
        <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/journal" onClick={onClose} />}>
          Abrir o jornal
        </Button>
        <Button variant="dark" size="sm" onClick={onClose}>
          Fechar
        </Button>
      </div>
    </Card>
  );
}
