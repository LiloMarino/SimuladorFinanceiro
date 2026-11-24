import { describe, expect, it } from "vitest";
import type { DebugCommand } from "@/types";
import { applyCompletion, completionOf } from "./completion";

const commands: DebugCommand[] = [
  {
    name: "add_cash",
    help: "soma ao caixa",
    arguments: [
      {
        name: "jogador",
        help: "apelido",
        required: true,
        choices: [
          { value: "murilo", label: null },
          { value: "marina", label: "bot" },
          { value: "ana", label: null },
        ],
      },
      { name: "valor", help: "em reais", required: true, choices: null },
    ],
  },
  { name: "give_stock", help: "põe ativos", arguments: [] },
  { name: "give_title", help: "aplica em título", arguments: [] },
];

describe("completionOf", () => {
  it("oferece os comandos na primeira palavra", () => {
    const { options, token } = completionOf("gi", commands);
    expect(token).toBe("gi");
    expect(options.map((o) => o.value)).toEqual(["give_stock", "give_title"]);
  });

  it("oferece todos os comandos na linha vazia", () => {
    expect(completionOf("", commands).options).toHaveLength(3);
  });

  it("oferece as escolhas do argumento depois do espaço", () => {
    const { options, token } = completionOf("add_cash ", commands);
    expect(token).toBe("");
    expect(options.map((o) => o.value)).toEqual(["murilo", "marina", "ana"]);
  });

  it("filtra a escolha pelo que foi digitado, sem distinguir maiúscula", () => {
    expect(completionOf("add_cash MA", commands).options.map((o) => o.value)).toEqual(["marina"]);
  });

  it("não oferece nada para argumento livre ou comando desconhecido", () => {
    expect(completionOf("add_cash murilo ", commands).options).toEqual([]);
    expect(completionOf("nada ", commands).options).toEqual([]);
  });
});

describe("applyCompletion", () => {
  it("completa a única opção com um espaço no fim", () => {
    expect(applyCompletion("add_c", completionOf("add_c", commands))).toBe("add_cash ");
    expect(applyCompletion("add_cash an", completionOf("add_cash an", commands))).toBe("add_cash ana ");
  });

  it("avança até o prefixo comum quando há várias opções", () => {
    expect(applyCompletion("g", completionOf("g", commands))).toBe("give_");
    expect(applyCompletion("add_cash m", completionOf("add_cash m", commands))).toBe("add_cash m");
    expect(applyCompletion("add_cash mari", completionOf("add_cash mari", commands))).toBe("add_cash marina ");
  });

  it("deixa a linha como está sem opção", () => {
    expect(applyCompletion("xyz", completionOf("xyz", commands))).toBe("xyz");
  });
});
