/** "Ligada" com o ponto verde: a estratégia que está operando. */
export function ActiveMark({ since }: { since?: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-success">
      <span className="size-2 rounded-full bg-success" />
      Ligada{since ? ` desde ${since}` : ""}
    </span>
  );
}
