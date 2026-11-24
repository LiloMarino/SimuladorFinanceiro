import { describe, expect, it } from "vitest";
import { stepHistory } from "./history";

const sent = ["add_cash ana 10", "help", "set_selic 13,75"];

describe("stepHistory", () => {
  it("a seta para cima volta do último comando ao primeiro e para nele", () => {
    const first = stepHistory(sent, 3, "up");
    expect(first).toEqual({ cursor: 2, line: "set_selic 13,75" });
    const second = stepHistory(sent, first.cursor, "up");
    expect(second).toEqual({ cursor: 1, line: "help" });
    expect(stepHistory(sent, 0, "up")).toEqual({ cursor: 0, line: "add_cash ana 10" });
  });

  it("a seta para baixo avança e termina na linha vazia", () => {
    expect(stepHistory(sent, 0, "down")).toEqual({ cursor: 1, line: "help" });
    expect(stepHistory(sent, 2, "down")).toEqual({ cursor: 3, line: "" });
    expect(stepHistory(sent, 3, "down")).toEqual({ cursor: 3, line: "" });
  });

  it("sem histórico a linha fica vazia", () => {
    expect(stepHistory([], 0, "up")).toEqual({ cursor: 0, line: "" });
  });
});
