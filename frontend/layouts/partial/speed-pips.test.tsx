import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { Kbd } from "@/shared/components/ui/kbd";
import { click, findElements } from "./element-tree";
import { SpeedPips } from "./speed-pips";

const bars = (tree: unknown) => findElements(tree, (element) => element.type === "button");

describe("velocidade em tracinhos", () => {
  it("um clique no tracinho pede a velocidade dele", () => {
    const onChange = vi.fn();
    const tree = SpeedPips({ speed: 1, resumeSpeed: 1, disabled: false, onChange });
    const labelled = (label: string) => bars(tree).find((bar) => bar.props["aria-label"] === label);

    click(labelled("Velocidade 4×"));
    click(labelled("Velocidade 100×"));

    expect(onChange.mock.calls).toEqual([[4], [100]]);
  });

  it("cada tracinho mostra a tecla dele na dica", () => {
    const tree = SpeedPips({ speed: 1, resumeSpeed: 1, disabled: false, onChange: vi.fn() });
    const keys = findElements(tree, (element) => element.type === Kbd && element.props["inverse"] === true)
      .map((element) => element.props["children"])
      .filter((key) => key !== "Espaço");

    expect(keys).toEqual([1, 2, 3, 4, 5]);
  });

  it("mostra a velocidade atual ao lado e marca só o tracinho dela", () => {
    const html = renderToStaticMarkup(<SpeedPips speed={10} resumeSpeed={1} disabled={false} onChange={vi.fn()} />);

    expect(html).toContain("10×</span>");
    expect(html.match(/aria-pressed="true"/g)).toHaveLength(1);
    expect(html).toContain('aria-label="Velocidade 10×" aria-pressed="true"');
  });

  it("na pausa nenhum tracinho está pressionado e o número guardado aparece apagado", () => {
    const html = renderToStaticMarkup(<SpeedPips speed={0} resumeSpeed={4} disabled={false} onChange={vi.fn()} />);

    expect(html).not.toContain('aria-pressed="true"');
    expect(html).toContain("text-sidebar-muted");
    expect(html).toContain("4×</span>");
  });
});
