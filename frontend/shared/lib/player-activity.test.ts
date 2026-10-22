import { describe, expect, it } from "vitest";
import { PLAYER_ACTIVITIES, activityForPath } from "./player-activity";

describe("activityForPath", () => {
  it.each([
    ["/lobby", "lobby"],
    ["/import-assets", "import_assets"],
    ["/compare-simulations", "compare_simulations"],
    ["/match-result/12", "match_result"],
    ["/settings", "settings"],
  ] as const)("%s é %s", (pathname, activity) => {
    expect(activityForPath(pathname)).toBe(activity);
  });

  it.each(["/", "/portfolio", "/variable-income/PETR4", "/login", "/join", "/nao-existe"])(
    "%s cai em menus",
    (pathname) => {
      expect(activityForPath(pathname)).toBe("menus");
    },
  );

  it("não confunde rota que só começa igual", () => {
    expect(activityForPath("/settings/extra")).toBe("menus");
    expect(activityForPath("/match-result")).toBe("menus");
  });

  it("toda atividade tem selo curto e dica", () => {
    for (const { label, hint } of Object.values(PLAYER_ACTIVITIES)) {
      expect(label.length).toBeGreaterThan(0);
      expect(hint.length).toBeGreaterThan(0);
    }
  });
});
