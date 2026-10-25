/** Ids dos tópicos do Como jogar, na ordem da lista; o registro em features/tutorial tem um tópico para cada. */
export const TOPIC_IDS = ["buy-stock", "order-types", "leverage"] as const;

export type TopicId = (typeof TOPIC_IDS)[number];
