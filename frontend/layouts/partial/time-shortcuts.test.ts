import { describe, expect, it } from "vitest";
import { isTypingTarget, shortcutFor, speedForShortcut } from "./time-shortcuts";

// Um alvo que responde ao `closest` achando o nome do elemento no seletor
const target = (name: string) => ({ closest: (selector: string) => (selector.includes(name) ? {} : null) });

const press = (key: string, overrides: Record<string, unknown> = {}) => ({
  key,
  ctrlKey: false,
  metaKey: false,
  altKey: false,
  repeat: false,
  defaultPrevented: false,
  target: target("body"),
  ...overrides,
});

describe("atalhos do tempo", () => {
  it("o Espaço pausa e retoma", () => {
    expect(shortcutFor(press(" "))).toEqual({ kind: "toggle-pause" });
  });

  it("as teclas 1 a 5 escolhem a velocidade de mesmo número", () => {
    // 1 → 1×, 2 → 2×, 3 → 4×, 4 → 10×, 5 → 100×
    const speeds = ["1", "2", "3", "4", "5"].map((key) => shortcutFor(press(key)));
    expect(speeds).toEqual([1, 2, 4, 10, 100].map((speed) => ({ kind: "speed", speed })));
  });

  it("as outras teclas não fazem nada", () => {
    expect(shortcutFor(press("6"))).toBeNull();
    expect(shortcutFor(press("0"))).toBeNull();
    expect(shortcutFor(press("a"))).toBeNull();
  });

  it("digitar num campo não aciona o tempo", () => {
    for (const tag of ["input", "textarea", "select", "contenteditable"]) {
      expect(isTypingTarget(target(tag))).toBe(true);
      expect(shortcutFor(press(" ", { target: target(tag) }))).toBeNull();
      expect(shortcutFor(press("3", { target: target(tag) }))).toBeNull();
    }
  });

  it("o Espaço com um botão em foco fica com o botão", () => {
    expect(shortcutFor(press(" ", { target: target("button") }))).toBeNull();
    expect(shortcutFor(press("3", { target: target("button") }))).toEqual({ kind: "speed", speed: 4 });
  });

  it("combinação com Ctrl, Cmd ou Alt, tecla repetida e tecla já tratada não acionam", () => {
    expect(shortcutFor(press("1", { ctrlKey: true }))).toBeNull();
    expect(shortcutFor(press("1", { metaKey: true }))).toBeNull();
    expect(shortcutFor(press(" ", { altKey: true }))).toBeNull();
    expect(shortcutFor(press(" ", { repeat: true }))).toBeNull();
    expect(shortcutFor(press(" ", { defaultPrevented: true }))).toBeNull();
  });

  it("o Espaço pausa a partida em andamento e retoma na velocidade guardada", () => {
    expect(speedForShortcut({ kind: "toggle-pause" }, 10, 4)).toBe(0);
    expect(speedForShortcut({ kind: "toggle-pause" }, 0, 4)).toBe(4);
    expect(speedForShortcut({ kind: "speed", speed: 100 }, 0, 4)).toBe(100);
  });
});
