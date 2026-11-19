import { describe, expect, it } from "vitest";
import {
  futureShareOf,
  hasScheduledChange,
  managerPointsAfter,
  myInviteOf,
  othersPoints,
  splitMonthly,
  type Comanager,
} from "./fund-comanagers";

const base: Comanager = {
  user_id: 2,
  status: "ACTIVE",
  share: "0.2000",
  pending_share: null,
  pending_from: null,
  invited_on: "2026-01-02",
  since: "2026-01-03",
  nickname: "Ana",
  color: null,
  expires_on: null,
};

describe("co-gestores da gestora", () => {
  it("a parte que vale daqui em diante é a agendada, senão a de hoje", () => {
    expect(futureShareOf(base)).toBeCloseTo(0.2, 9);
    expect(futureShareOf({ share: "0.2000", pending_share: "0.3000" })).toBeCloseTo(0.3, 9);
  });

  it("os outros reservam a parte futura deles, sem contar o próprio co-gestor", () => {
    const bia: Comanager = { ...base, user_id: 3, share: "0.1000", pending_share: "0.1500" };
    expect(othersPoints([base, bia], null)).toBeCloseTo(35, 9);
    expect(othersPoints([base, bia], 2)).toBeCloseTo(15, 9);
  });

  it("a parte do principal é o que sobra das partes dos co-gestores", () => {
    expect(managerPointsAfter(15, 20)).toBe(65);
  });

  it("a taxa mensal arredonda a parte do co-gestor para baixo e o principal fica com o resto", () => {
    // 20% de R$ 1.666,67 = R$ 333,334: o co-gestor leva R$ 333,33 e o principal R$ 1.333,34
    expect(splitMonthly(1666.67, 20)).toEqual({ comanager: 333.33, manager: 1333.34 });
  });

  it("só o co-gestor ativo com parte e data marcadas tem mudança agendada", () => {
    expect(hasScheduledChange(base)).toBe(false);
    expect(hasScheduledChange({ ...base, pending_share: "0.3000", pending_from: "2026-02-02" })).toBe(true);
    expect(hasScheduledChange({ ...base, status: "INVITED", pending_share: "0.3000", pending_from: null })).toBe(false);
  });

  it("o convite do jogador é a linha pendente dele", () => {
    const invited: Comanager = { ...base, user_id: 5, status: "INVITED" };
    expect(myInviteOf({ comanagers: [base, invited] }, 5)).toBe(invited);
    expect(myInviteOf({ comanagers: [base, invited] }, 2)).toBeUndefined();
  });
});
