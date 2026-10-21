import { describe, expect, it } from "vitest";
import { summarizeAssistances } from "./assistance";

describe("summarizeAssistances", () => {
  it("é Normal com todas as ajudas aparecendo", () => {
    expect(summarizeAssistances([true, true])).toEqual({ mode: "NORMAL", shown: 2, total: 2 });
  });

  it("é Especialista com todas escondidas", () => {
    expect(summarizeAssistances([false, false])).toEqual({ mode: "EXPERT", shown: 0, total: 2 });
  });

  it("é Personalizado quando só uma está escondida, e conta as que seguem ligadas", () => {
    expect(summarizeAssistances([true, false])).toEqual({ mode: "CUSTOM", shown: 1, total: 2 });
    expect(summarizeAssistances([false, true])).toEqual({ mode: "CUSTOM", shown: 1, total: 2 });
  });
});
