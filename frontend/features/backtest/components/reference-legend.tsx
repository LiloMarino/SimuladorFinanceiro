type ReferenceLegendProps = {
  /** Texto curto, na mesma linha da legenda */
  compact?: boolean;
};

/** As referências do gráfico: CDI tracejado e Ibovespa pontilhado, que não ocupam vaga. */
export function ReferenceLegend({ compact = false }: ReferenceLegendProps) {
  return (
    <div className={compact ? "flex flex-wrap items-center gap-4 text-[13px]" : "grid gap-2"}>
      <span className="text-sm font-medium text-muted-foreground">Comparadas com</span>
      <div className="flex flex-wrap items-center gap-4 text-[13px]">
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden="true" className="w-[18px] border-t-2 border-dashed border-foreground" />
          CDI
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden="true" className="w-[18px] border-t-2 border-dotted border-faint-foreground" />
          Ibovespa
        </span>
        <span className="text-xs text-muted-foreground">
          {compact ? "linhas de referência, sem vaga" : "Linhas de referência no gráfico e no ranking. Não ocupam vaga."}
        </span>
      </div>
    </div>
  );
}
