/** As teclas que abrem e fecham o console: crase, acento agudo e til, inclusive como tecla morta do ABNT2. */
export function isToggleKey(event: Pick<KeyboardEvent, "key" | "code">): boolean {
  if (event.code === "Backquote") return true;
  if (event.key === "`" || event.key === "´" || event.key === "~") return true;
  return event.key === "Dead" && event.code === "BracketLeft";
}
