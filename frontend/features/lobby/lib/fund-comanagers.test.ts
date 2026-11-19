import { describe, expect, it } from "vitest";
import { openComanagers, pointsToShare, reservedPoints, sharePercent, type FundComanagerRow } from "./fund-comanagers";

const row = (nickname: string, share: string, status: FundComanagerRow["status"]): FundComanagerRow => ({
  nickname,
  share,
  status,
});

describe("fund-comanagers", () => {
  it("mostra a parte da API em porcentagem", () => {
    expect(sharePercent("0.2000")).toBe("20%");
    expect(sharePercent("0.125")).toBe("12.5%");
  });

  it("o convite recusado não ocupa vaga nem reserva parte", () => {
    const rows = [row("Duda", "0.2", "INVITED"), row("Caio", "0.3", "ACCEPTED"), row("Eva", "0.4", "DECLINED")];
    expect(openComanagers(rows).map((c) => c.nickname)).toEqual(["Duda", "Caio"]);
    expect(reservedPoints(rows)).toBe(50);
  });

  it("converte os pontos para a fração da API", () => {
    expect(pointsToShare(20)).toBe("0.2");
    expect(pointsToShare(57)).toBe("0.57");
  });
});
