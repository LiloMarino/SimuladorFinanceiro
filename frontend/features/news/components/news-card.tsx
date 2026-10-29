import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import type { News } from "@/types";
import { NewsKicker, NewsMasthead } from "./news-parts";

type NewsCardProps = {
  news: News;
  /** Quantas outras manchetes chegaram no mesmo pregão */
  others: number;
};

/** O cartão de papel com a manchete do pregão, duas linhas no máximo; o texto inteiro está no jornal. */
export function NewsCard({ news, others }: NewsCardProps) {
  return (
    <Card variant="paper" size="flush" role="status" className="w-[360px]">
      <NewsMasthead date={news.news_date} />
      <div className="grid gap-1 px-3.5 pt-2.5 pb-3">
        <NewsKicker type={news.news_type} />
        <p className="line-clamp-2 font-serif text-[17px] leading-snug font-semibold">{news.headline}</p>
        {news.dek && <p className="line-clamp-2 text-[13px] text-muted-foreground">{news.dek}</p>}
      </div>
      <div className="flex items-center justify-between border-t border-paper-border px-3.5 py-1.5 text-xs">
        <span className="text-muted-foreground">{others > 0 && `+${others} neste pregão`}</span>
        <Button variant="link" size="xs" nativeButton={false} render={<Link to="/journal" />}>
          Abrir o jornal ›
        </Button>
      </div>
    </Card>
  );
}
