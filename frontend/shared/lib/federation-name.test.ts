import { describe, expect, it } from "vitest";
import { defaultFederationName } from "./federation-name";

describe("defaultFederationName", () => {
  it("junta as siglas com travessão", () => {
    expect(defaultFederationName("PTD", "NOV")).toBe("Federação PTD–NOV");
  });
});
