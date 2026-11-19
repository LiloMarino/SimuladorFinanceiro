import { describe, expect, it } from "vitest";
import type { FundRoomItem, Pending } from "@/types";
import {
  isHeldBy,
  managedHint,
  operates,
  roomBlocks,
  roomLostFund,
  roomNetWorth,
  roomPendingCount,
  roomShareOf,
  roomTotalNetWorth,
} from "./fund-room";

const ME = 7;

const fund = (over: Partial<FundRoomItem>): FundRoomItem =>
  ({
    id: 1,
    manager_user_id: 1,
    founder_user_id: 1,
    leave_manager_user_id: null,
    frozen_until: null,
    automatic: false,
    manager_since: null,
    i_comanage: false,
    my_quotas: "0",
    quotas: "1000",
    nav: "100",
    ...over,
  }) as FundRoomItem;

describe("roomBlocks", () => {
  it("põe a gestora que o jogador gere, a que está em licença, a das cotas e as outras cada uma no seu bloco", () => {
    const managed = fund({ id: 1, manager_user_id: ME });
    const onLeave = fund({ id: 2, manager_user_id: 3, leave_manager_user_id: ME });
    const quotas = fund({ id: 3, my_quotas: "10" });
    const other = fund({ id: 4 });

    const blocks = roomBlocks([managed, onLeave, quotas, other], ME);

    expect(blocks.managed.map((f) => f.id)).toEqual([1, 2]);
    expect(blocks.quotas.map((f) => f.id)).toEqual([3]);
    expect(blocks.others.map((f) => f.id)).toEqual([4]);
  });

  it("a gestora que o jogador gere fica só no bloco dela, mesmo com cotas", () => {
    const mine = fund({ manager_user_id: ME, my_quotas: "500" });

    const blocks = roomBlocks([mine], ME);

    expect(blocks.managed).toHaveLength(1);
    expect(blocks.quotas).toHaveLength(0);
  });
});

describe("isHeldBy", () => {
  it("vale para quem gere e para quem está em licença, não para os outros", () => {
    expect(isHeldBy(fund({ manager_user_id: ME }), ME)).toBe(true);
    expect(isHeldBy(fund({ leave_manager_user_id: ME }), ME)).toBe(true);
    expect(isHeldBy(fund({}), ME)).toBe(false);
  });
});

describe("patrimônio e parte", () => {
  it("o patrimônio é o patrimônio por cota vezes as cotas, e nulo sem patrimônio por cota", () => {
    expect(roomNetWorth(fund({ nav: "110.44", quotas: "1000" }))).toBeCloseTo(110440);
    expect(roomNetWorth(fund({ nav: null }))).toBeNull();
  });

  it("a soma ignora a gestora sem patrimônio por cota", () => {
    expect(roomTotalNetWorth([fund({ nav: "10", quotas: "100" }), fund({ nav: null })])).toBe(1000);
  });

  it("a parte do jogador é a fração das cotas, e zero sem cotas em circulação", () => {
    expect(roomShareOf(fund({ my_quotas: "250", quotas: "1000" }))).toBe(0.25);
    expect(roomShareOf(fund({ my_quotas: "0", quotas: "0" }))).toBe(0);
  });
});

describe("co-gestor", () => {
  it("opera a gestora e a vê no bloco dela, sem que isso conte como ter gestora para fundar", () => {
    const comanaged = fund({ id: 1, i_comanage: true, my_quotas: "10" });

    expect(operates(comanaged, ME)).toBe(true);
    expect(isHeldBy(comanaged, ME)).toBe(false);
    expect(roomBlocks([comanaged], ME).managed).toHaveLength(1);
  });
});

describe("roomLostFund", () => {
  it("é a gestora fundada pelo jogador que ele não gere, enquanto ele não tem outra", () => {
    const lost = fund({ id: 1, founder_user_id: ME, manager_user_id: 3 });

    expect(roomLostFund([lost], ME)?.id).toBe(1);
    expect(roomLostFund([lost, fund({ id: 2, manager_user_id: ME, founder_user_id: ME })], ME)).toBeUndefined();
    expect(roomLostFund([lost], 99)).toBeUndefined();
  });

  it("a gestora em licença não está perdida: ela volta", () => {
    expect(
      roomLostFund([fund({ founder_user_id: ME, manager_user_id: 3, leave_manager_user_id: ME })], ME),
    ).toBeUndefined();
  });
});

describe("managedHint", () => {
  it("diz que a gestora congela enquanto o jogador é presidente sem co-gestor nem estratégia", () => {
    const frozen = fund({ manager_user_id: ME, frozen_until: "2027-12-31" });

    expect(managedHint([frozen], ME)).toBe(
      "A gestora congela enquanto você é presidente, a menos que tenha co-gestor ou estratégia ligada.",
    );
  });

  it("diz que a gestora segue no automático quando a presidência tem estratégia ligada", () => {
    const automatic = fund({ manager_user_id: ME, frozen_until: "2027-12-31", automatic: true });

    expect(managedHint([automatic], ME)).toBe("A gestora segue no automático enquanto você é presidente.");
  });

  it("diz que a gestora está com o co-gestor quando ela passou ao herdeiro", () => {
    const onLeave = fund({ manager_user_id: 3, leave_manager_user_id: ME });

    expect(managedHint([onLeave], ME)).toBe("A gestora está com o co-gestor até o fim do mandato.");
  });

  it("conta a gestora ganha na assembleia, e não a recebida do presidente", () => {
    const won = fund({ name: "Boreal", manager_user_id: ME, founder_user_id: 3, manager_since: "2023-11-10" });
    const inherited = fund({
      manager_user_id: ME,
      founder_user_id: 3,
      leave_manager_user_id: 3,
      manager_since: "2023-11-10",
    });

    expect(managedHint([won], ME)).toBe("Ganhou a assembleia da Boreal em 10 nov.");
    expect(managedHint([inherited], ME)).toBe("Abrir leva à tela de gestão, com as abas da gestora.");
  });
});

describe("roomPendingCount", () => {
  const item = (over: Partial<Pending>): Pending => ({ fund_id: 1, type: "FUND_ASSEMBLY_VOTE", ...over }) as Pending;

  it("conta as decisões da gestora e ignora as de outras e as que não são decisão", () => {
    const pending = [
      item({}),
      item({ type: "DIRECTED_ISSUANCE_OFFER" }),
      item({ fund_id: 2 }),
      item({ type: "NEGATIVE_CASH" }),
    ];

    expect(roomPendingCount(pending, 1)).toBe(2);
  });
});
