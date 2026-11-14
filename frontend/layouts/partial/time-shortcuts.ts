/** As velocidades da partida, da mais lenta à mais rápida; a tecla 1 a 5 escolhe a de mesmo número. */
export const SPEED_OPTIONS = [1, 2, 4, 10, 100] as const;
export const MAX_SPEED = 100;

export type TimeShortcut = { kind: "toggle-pause" } | { kind: "speed"; speed: number };

type ShortcutEvent = {
  key: string;
  ctrlKey: boolean;
  metaKey: boolean;
  altKey: boolean;
  repeat: boolean;
  defaultPrevented: boolean;
  target: unknown;
};

const TYPING_FIELD = "input, textarea, select, [contenteditable]:not([contenteditable='false'])";
// O que já tem ação própria no Espaço (ativar o botão, o link ou o item)
const ACTIVATABLE =
  "button, a[href], summary, [role='button'], [role='menuitem'], [role='option'], [role='tab'], [role='switch'], [role='checkbox'], [role='radio']";

function matchesClosest(target: unknown, selector: string) {
  const closest = (target as { closest?: (selector: string) => unknown } | null)?.closest;
  return typeof closest === "function" && closest.call(target, selector) !== null;
}

/** O alvo do evento é um campo onde o jogador digita. */
export function isTypingTarget(target: unknown) {
  return matchesClosest(target, TYPING_FIELD);
}

/**
 * A ação do teclado sobre o tempo: Espaço pausa e retoma, 1 a 5 escolhem a velocidade.
 * Digitando em um campo, ou com a tecla já tratada por outro, não há ação; o Espaço também
 * fica com o botão, link ou item em foco.
 */
export function shortcutFor(event: ShortcutEvent): TimeShortcut | null {
  if (event.defaultPrevented || event.repeat || event.ctrlKey || event.metaKey || event.altKey) return null;
  if (isTypingTarget(event.target)) return null;

  if (event.key === " ") {
    return matchesClosest(event.target, ACTIVATABLE) ? null : { kind: "toggle-pause" };
  }

  const speed = SPEED_OPTIONS[Number(event.key) - 1];
  return /^[1-5]$/.test(event.key) && speed !== undefined ? { kind: "speed", speed } : null;
}

/** A velocidade que o atalho pede: o Espaço pausa (0) ou retoma na velocidade guardada. */
export function speedForShortcut(shortcut: TimeShortcut, currentSpeed: number, resumeSpeed: number) {
  if (shortcut.kind === "speed") return shortcut.speed;
  return currentSpeed === 0 ? resumeSpeed : 0;
}
