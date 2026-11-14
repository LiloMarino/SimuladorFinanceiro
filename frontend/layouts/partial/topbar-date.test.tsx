import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { TopbarDate } from "./topbar-date";

describe("data da topbar", () => {
  it("na pausa vira 'Pausado · data' sobre fundo âmbar", () => {
    const html = renderToStaticMarkup(<TopbarDate date="14 mar 2023" paused maxSpeed={false} pauseHint={null} />);

    expect(html).toContain("Pausado · ");
    expect(html).toContain("14 mar 2023");
    expect(html).toContain("bg-warning-soft");
    expect(html).toContain('role="status"');
  });

  it("em andamento é só a data, sem a palavra Pausado", () => {
    const html = renderToStaticMarkup(
      <TopbarDate date="14 mar 2023" paused={false} maxSpeed={false} pauseHint={null} />,
    );

    expect(html).not.toContain("Pausado");
    expect(html).not.toContain("bg-warning-soft");
  });

  it("a 100× a data fica azul", () => {
    const html = renderToStaticMarkup(<TopbarDate date="14 mar 2023" paused={false} maxSpeed pauseHint={null} />);

    expect(html).toContain("bg-info-soft");
  });

  it("antes do primeiro dado mostra o traço", () => {
    const html = renderToStaticMarkup(<TopbarDate date={undefined} paused={false} maxSpeed={false} pauseHint={null} />);

    expect(html).toContain("—");
  });
});
