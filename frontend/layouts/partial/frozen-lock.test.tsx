import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { frozenHint } from "./frozen-hint";
import { FrozenLock } from "./frozen-lock";

describe("cadeado da carteira congelada", () => {
  it("o cadeado se anuncia com o último dia do congelamento", () => {
    const html = renderToStaticMarkup(<FrozenLock until="2023-01-01" severalAccounts />);

    expect(html).toContain('aria-label="Congelada até 01/01/2023"');
  });

  it("a dica traz a data e explica o bloqueio", () => {
    const { title, body } = frozenHint("2023-01-01", true);

    expect(title).toBe("Congelada até 01/01/2023");
    expect(body).toContain("suas contas ficam paradas");
    expect(body).toContain("comprar e vender estão bloqueados");
  });

  it("sem gestoras a dica fala da carteira única", () => {
    expect(frozenHint("2023-01-01", false).body).toContain("sua carteira fica parada");
  });
});
