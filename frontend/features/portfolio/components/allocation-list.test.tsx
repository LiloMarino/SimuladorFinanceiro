import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { AllocationRow } from "@/features/portfolio/lib/allocation-rows";
import { AllocationList } from "./allocation-list";

const row = (label: string, exitRule?: string): AllocationRow => ({
  label,
  value: "1000",
  pct: "0.25",
  color: "bg-chart-7",
  ...(exitRule ? { exitRule } : {}),
});

describe("AllocationList", () => {
  it("usa colunas de no mínimo 160 px, sem quantidade fixa", () => {
    const html = renderToStaticMarkup(<AllocationList rows={[row("A"), row("B"), row("C"), row("D"), row("E")]} />);
    expect(html).toContain("grid-cols-[repeat(auto-fill,minmax(160px,1fr))]");
    expect(html).not.toMatch(/grid-cols-[34]\b/);
  });

  it("mostra a regra de saída só nas linhas que a têm", () => {
    const html = renderToStaticMarkup(<AllocationList rows={[row("Caixa"), row("FGTS", "Sai na demissão")]} />);
    expect(html).toContain("Como sai o FGTS");
    expect(html).not.toContain("Como sai o Caixa");
  });
});
