import { useState, type PropsWithChildren } from "react";
import { TutorialDialog } from "../components/tutorial-dialog";
import { topicList } from "../lib/topics";
import type { TopicId } from "@/shared/lib/tutorial-topic-ids";
import { unseenTopics } from "../lib/tutorial-progress";
import {
  loadTutorialState,
  markNudged,
  markSeen,
  saveTutorialState,
  type TutorialState,
  type TutorialStyle,
} from "@/shared/lib/tutorial-storage";
import { TutorialContext } from "@/shared/context/tutorial";

export function TutorialProvider({ children }: PropsWithChildren) {
  const [state, setState] = useState(loadTutorialState);
  const [isOpen, setIsOpen] = useState(false);
  const [topicId, setTopicId] = useState<TopicId>(topicList[0].id);
  const [origin, setOrigin] = useState<string | null>(null);

  const update = (next: TutorialState) => {
    setState(next);
    saveTutorialState(next);
  };

  // Abrir o tópico é vê-lo
  const open = (requested?: TopicId, from?: string) => {
    const target = requested ?? (unseenTopics(state, topicList)[0] ?? topicList[0]).id;
    update(markSeen({ ...state, opened: true }, target));
    setTopicId(target);
    setOrigin(from ?? null);
    setIsOpen(true);
  };

  const select = (target: TopicId) => {
    update(markSeen(state, target));
    setTopicId(target);
  };

  return (
    <TutorialContext.Provider
      value={{
        state,
        isOpen,
        topicId,
        origin,
        unseenCount: unseenTopics(state, topicList).length,
        open,
        close: () => setIsOpen(false),
        select,
        setStyle: (style: TutorialStyle) => update({ ...state, style }),
        setCollapsed: (collapsed) => update({ ...state, collapsed }),
        answerNudge: (answered) => update(markNudged(state, answered)),
      }}
    >
      {children}
      <TutorialDialog />
    </TutorialContext.Provider>
  );
}
