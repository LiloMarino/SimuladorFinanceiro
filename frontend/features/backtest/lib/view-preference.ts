export type ParticipantsView = "list" | "cards";

const STORAGE_KEY = "backtest-participants-view";

/** O jeito de ver as estratégias fica no navegador: o próximo backtest abre como o último. */
export function loadViewPreference(): ParticipantsView {
  try {
    return localStorage.getItem(STORAGE_KEY) === "cards" ? "cards" : "list";
  } catch {
    return "list";
  }
}

export function saveViewPreference(view: ParticipantsView) {
  try {
    localStorage.setItem(STORAGE_KEY, view);
  } catch {
    // Sem armazenamento (aba privada, dados bloqueados): a escolha só não é lembrada
  }
}
