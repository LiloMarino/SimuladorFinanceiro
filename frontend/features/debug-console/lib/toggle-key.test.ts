import { describe, expect, it } from "vitest";
import { isToggleKey } from "./toggle-key";

describe("isToggleKey", () => {
  it("aceita crase, acento agudo, til e a tecla morta do ABNT2", () => {
    expect(isToggleKey({ key: "`", code: "Backquote" })).toBe(true);
    expect(isToggleKey({ key: "´", code: "BracketLeft" })).toBe(true);
    expect(isToggleKey({ key: "~", code: "Backquote" })).toBe(true);
    expect(isToggleKey({ key: "Dead", code: "BracketLeft" })).toBe(true);
  });

  it("recusa as demais teclas", () => {
    expect(isToggleKey({ key: "a", code: "KeyA" })).toBe(false);
    expect(isToggleKey({ key: "Dead", code: "KeyE" })).toBe(false);
  });
});
