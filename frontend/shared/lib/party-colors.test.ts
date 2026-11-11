import { describe, expect, it } from "vitest";
import { contrastRatio, deltaE2000 } from "./color-math";
import {
  COMPUTER_COLORS,
  NO_COLOR,
  PARTY_PALETTE,
  defaultPartyColor,
  partyColor,
  partyForeground,
} from "./party-colors";
import { INK, MAX_PLAYERS, PLAYER_COLORS, WHITE } from "./player-colors";

// Fundos do tema claro (index.css) e as duas cores de texto, em hex
const BACKGROUNDS = ["#F4F5F7", "#FFFFFF", "#EEF0F3"];
const TEXT_HEX = { [WHITE]: "#FFFFFF", [INK]: "#0F1729" };

// Contraste mínimo contra o fundo: 3 para 1 em toda cor; o âmbar, que é o amarelo da paleta, fica em 2,5
const MIN_CONTRAST: Record<string, number> = { "#CC8A00": 2.5 };
const minContrast = (hex: string) => MIN_CONTRAST[hex] ?? 3;

describe("PARTY_PALETTE", () => {
  it("tem 20 cores, todas com hex único", () => {
    expect(PARTY_PALETTE).toHaveLength(20);
    expect(new Set(PARTY_PALETTE.map((c) => c.value)).size).toBe(20);
  });

  it("começa pelas cores dos jogadores e tem mais cores que a sala tem vagas", () => {
    expect(PARTY_PALETTE.slice(0, MAX_PLAYERS).map((c) => c.value)).toEqual(PLAYER_COLORS.map((c) => c.hex));
    expect(PARTY_PALETTE.length).toBeGreaterThan(MAX_PLAYERS);
  });

  it.each(PARTY_PALETTE)(
    "$name se vê em todo fundo do app (contraste de pelo menos 3 para 1, 2,5 no âmbar)",
    (color) => {
      for (const background of BACKGROUNDS) {
        expect(contrastRatio(color.value, background)).toBeGreaterThanOrEqual(minContrast(color.value));
      }
    },
  );

  it.each(PARTY_PALETTE)("a sigla sobre $name tem pelo menos 4,5 para 1 de contraste", (color) => {
    const text = TEXT_HEX[color.foreground as keyof typeof TEXT_HEX];
    expect(contrastRatio(color.value, text)).toBeGreaterThanOrEqual(4.5);
  });

  it.each(PARTY_PALETTE)("$name se distingue das outras cores (ΔE de pelo menos 12)", (color) => {
    const others = [
      ...PARTY_PALETTE.filter((c) => c.value !== color.value).map((c) => c.value),
      ...Object.values(COMPUTER_COLORS),
      NO_COLOR,
    ];
    for (const other of others) {
      expect(deltaE2000(color.value, other), `${color.value} contra ${other}`).toBeGreaterThanOrEqual(12);
    }
  });
});

describe("partyColor", () => {
  it("usa a cor do partido de jogador e a paleta fixa no do computador", () => {
    expect(partyColor({ abbr: "PRL", color: "#15803D" })).toBe("#15803D");
    expect(partyColor({ abbr: "UPR", color: null })).toBe("#6B6B6B");
    expect(partyColor({ abbr: "ACI", color: null })).toBe("#0F7C9C");
    expect(partyColor({ abbr: "MNV", color: null })).toBe("#7E6B17");
  });
});

describe("partyForeground", () => {
  it("segue o texto da cor da paleta de mesmo hex e deixa branco fora dela", () => {
    expect(partyForeground("#209993")).toBe(INK);
    expect(partyForeground("#2350D8")).toBe(WHITE);
    expect(partyForeground("#e8590c")).toBe(INK);
    expect(partyForeground("#15803D")).toBe(WHITE);
  });
});

describe("defaultPartyColor", () => {
  it("marca a cor de quem funda quando está livre", () => {
    expect(defaultPartyColor("chart-3", [])).toBe("#7E9314");
  });

  it("cai na 1ª cor livre quando outro partido já usa a de quem funda", () => {
    expect(defaultPartyColor("chart-1", ["#2350d8"])).toBe("#209993");
    expect(defaultPartyColor(undefined, [])).toBe("#2350D8");
  });

  it("alcança as cores só de partido quando as dos jogadores estão tomadas", () => {
    const taken = PARTY_PALETTE.slice(0, MAX_PLAYERS).map((c) => c.value);
    expect(defaultPartyColor("chart-1", taken)).toBe("#D92D20");
  });
});
