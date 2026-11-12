import { describe, expect, it } from "vitest";
import { growthTone } from "./country";

describe("growthTone", () => {
  it("separa bom, fraco e recessão nas fronteiras de 2% e 0%", () => {
    expect(growthTone(0.021)).toBe("good");
    expect(growthTone(0.02)).toBe("good");
    expect(growthTone(0.0199)).toBe("weak");
    expect(growthTone(0)).toBe("weak");
    expect(growthTone(-0.0001)).toBe("recession");
  });
});
