import type { NewsSection, NewsType, NotificationCatalog } from "@/types";

/** A cor do rótulo de cada seção, nas manchetes e nas abas. */
export const SECTION_TONE: Record<NewsSection, string> = {
  ECONOMY: "text-info",
  COMPANIES: "text-success",
  POLITICS: "text-secret",
  HISTORY: "text-warning",
};

/** A seção de um tipo de manchete, pelo registro. */
export function sectionOf(catalog: NotificationCatalog, type: NewsType) {
  return catalog.news.find((spec) => spec.type === type)?.section;
}

/** O nome da seção para o jogador. */
export function sectionLabel(catalog: NotificationCatalog, section: NewsSection) {
  return catalog.sections.find((spec) => spec.section === section)?.label ?? section;
}

/** A posição do tipo na ordem de importância do registro: quanto menor, mais importante. */
export function rankOf(catalog: NotificationCatalog, type: NewsType) {
  const index = catalog.news.findIndex((spec) => spec.type === type);
  return index === -1 ? catalog.news.length : index;
}
