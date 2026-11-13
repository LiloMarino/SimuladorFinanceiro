import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { contrastRatio } from "./color-math";

const css = readFileSync(resolve(import.meta.dirname, "../../index.css"), "utf-8");

// Valor hex de um token do :root (index.css)
const token = (name: string) => {
  const match = css.match(new RegExp(`^\\s*--${name}:\\s*(#[0-9a-fA-F]{6});`, "m"));
  if (!match) throw new Error(`Token --${name} não encontrado no :root do index.css`);
  return match[1] as string;
};

// Fundos onde a etiqueta aparece: card comum, card de bot e card do próprio jogador
const CARD_BACKGROUNDS = ["card", "subtle", "info-soft"];

describe("variante label do Badge", () => {
  it.each(CARD_BACKGROUNDS)("a borda tem pelo menos 3 para 1 de contraste contra o fundo --%s", (background) => {
    expect(contrastRatio(token("label-border"), token(background))).toBeGreaterThanOrEqual(3);
  });
});
