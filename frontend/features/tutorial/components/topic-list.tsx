import { useState } from "react";
import { BookOpen, Check } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import { useTutorial } from "@/shared/hooks/useTutorial";
import { groups, groupTopics, topicList, type RegisteredTopic } from "../lib/topics";
import { isSeen, unseenTopics } from "../lib/tutorial-progress";

/** Lista de tópicos da janela, agrupada; o ponto azul marca o que ainda não foi aberto. */
export function TopicList() {
  const { state, topicId, select } = useTutorial();
  const [collapsed, setCollapsed] = useState<string[]>([]);

  const toggle = (key: string) =>
    setCollapsed((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));

  const row = (topic: RegisteredTopic) => {
    const current = topic.id === topicId;
    return (
      <button
        key={topic.id}
        type="button"
        title={topic.title}
        aria-current={current ? "page" : undefined}
        className={cn(
          "flex h-10 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-sm hover:bg-muted",
          current && "bg-info-soft font-semibold text-info hover:bg-info-soft",
        )}
        onClick={() => select(topic.id)}
      >
        {topic.kind === "concept" && <BookOpen className="size-3.25 shrink-0 text-faint-foreground" />}
        <span className="min-w-0 truncate">{topic.title}</span>
        {!current && (
          <span className="ml-auto">
            {isSeen(state, topic) ? (
              <Check className="size-3.5 text-success" aria-label="Visto" />
            ) : (
              <span className="block size-2 rounded-full bg-primary" role="img" aria-label="Para ver" />
            )}
          </span>
        )}
      </button>
    );
  };

  return (
    <nav aria-label="Tópicos" className="flex w-70 shrink-0 flex-col gap-0.5 overflow-y-auto border-r px-3 pt-2 pb-4">
      {groupTopics(topicList).map(({ key, topics }) => {
        const [only] = topics;
        if (only && topics.length === 1) return row(only);

        const { label, icon: Icon } = groups[key];
        const open = !collapsed.includes(key);
        const unseen = unseenTopics(state, topics).length;
        return (
          <div key={key} className="grid gap-0.5">
            <button
              type="button"
              aria-expanded={open}
              className="flex h-10 items-center gap-2 rounded-lg px-2.5 text-sm font-semibold hover:bg-muted"
              onClick={() => toggle(key)}
            >
              <Icon className="size-3.5 text-muted-foreground" />
              <span className="min-w-0 truncate">{label}</span>
              <span className="ml-auto">
                {unseen > 0 ? (
                  <Badge variant="info" size="sm" numeric>
                    {unseen}
                  </Badge>
                ) : (
                  <Check className="size-3.5 text-success" aria-label="Tudo visto" />
                )}
              </span>
            </button>
            {open && <div className="ml-4 grid gap-0.5 border-l pl-1.5">{topics.map(row)}</div>}
          </div>
        );
      })}
    </nav>
  );
}
