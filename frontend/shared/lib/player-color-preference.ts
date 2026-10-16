const STORAGE_KEY = "player-color";

/** A última cor escolhida fica no navegador: vale em qualquer sala que o jogador entrar. */
export function loadColorPreference(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function saveColorPreference(color: string) {
  try {
    localStorage.setItem(STORAGE_KEY, color);
  } catch {
    // Sem armazenamento (aba privada, dados bloqueados): a cor só não é lembrada
  }
}
