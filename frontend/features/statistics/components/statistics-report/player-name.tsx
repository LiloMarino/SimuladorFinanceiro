/** Nome do jogador em linhas e cabeçalhos: quem está vendo aparece como "Você" em negrito, com o nome pequeno ao lado. */
export function PlayerName({ label, isYou }: { label: string; isYou: boolean }) {
  if (!isYou) return <>{label}</>;
  // Entre simulações o rótulo já nasce como "Você · A"
  if (label.startsWith("Você")) return <b>{label}</b>;
  return (
    <>
      <b>Você</b> <span className="text-xs font-normal text-faint-foreground">{label}</span>
    </>
  );
}
