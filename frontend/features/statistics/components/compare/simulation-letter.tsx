/** A letra da simulação na cor dela; sem letra, um quadrado vazio de quem ainda não foi escolhida. */
export function SimulationLetter({ letter, color }: { letter: string | null; color: string }) {
  return letter ? (
    <span
      className="grid size-6 shrink-0 place-content-center rounded-md font-mono text-xs font-semibold text-white"
      style={{ backgroundColor: color }}
    >
      {letter}
    </span>
  ) : (
    <span className="size-6 shrink-0 rounded-md border border-dashed border-input" aria-hidden="true" />
  );
}
