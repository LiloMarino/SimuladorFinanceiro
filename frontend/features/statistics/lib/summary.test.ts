import { describe, expect, it } from "vitest";
import { summaryTitle } from "./summary";

describe("summaryTitle", () => {
  it("nomeia a retrospectiva pelo ano", () => {
    expect(summaryTitle({ year: 2002 })).toBe("Retrospectiva de 2002");
  });
});
