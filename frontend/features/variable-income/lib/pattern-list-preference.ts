const STORAGE_KEY = "candle-pattern-list-open";

/** A lista dos padrões abre como o jogador a deixou da última vez. */
export function loadListOpen(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

export function saveListOpen(open: boolean) {
  try {
    localStorage.setItem(STORAGE_KEY, String(open));
  } catch {
    // Sem armazenamento (aba privada, dados bloqueados): a escolha só não é lembrada
  }
}
