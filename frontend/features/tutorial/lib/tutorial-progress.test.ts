import { describe, expect, it } from "vitest";
import { countHumans, nudgeTopicFor, shouldPause, shouldResume, unseenTopics } from "./tutorial-progress";
import { EMPTY_TUTORIAL_STATE, markNudged, markSeen, parseTutorialState } from "./tutorial-storage";

const topics = [
  { id: "a", screens: ["/variable-income"] },
  { id: "b", screens: ["/variable-income/:ticker"] },
  { id: "c", screens: ["/variable-income"] },
];

describe("estado guardado", () => {
  it("abre vazio quando não há nada guardado ou o texto está quebrado", () => {
    expect(parseTutorialState(null)).toEqual(EMPTY_TUTORIAL_STATE);
    expect(parseTutorialState("{quebrado")).toEqual(EMPTY_TUTORIAL_STATE);
  });

  it("descarta o campo fora do formato e mantém o resto", () => {
    const state = parseTutorialState(JSON.stringify({ seen: ["a"], nudged: "x", style: "inexistente", opened: true }));
    expect(state).toEqual({ ...EMPTY_TUTORIAL_STATE, seen: ["a"], opened: true });
  });

  it("marcar duas vezes o mesmo tópico não repete o id", () => {
    const once = markSeen(EMPTY_TUTORIAL_STATE, "a");
    expect(markSeen(once, "a").seen).toEqual(["a"]);
    expect(markNudged(EMPTY_TUTORIAL_STATE, "a").nudged).toEqual(["a"]);
  });
});

describe("tópicos não vistos", () => {
  it("conta os que o jogador ainda não abriu", () => {
    expect(unseenTopics(markSeen(EMPTY_TUTORIAL_STATE, "a"), topics).map((t) => t.id)).toEqual(["b", "c"]);
  });
});

describe("aviso da tela", () => {
  it("oferece o primeiro tópico da rota que ainda não foi visto nem avisado", () => {
    expect(nudgeTopicFor(EMPTY_TUTORIAL_STATE, topics, "/variable-income")?.id).toBe("a");
    expect(nudgeTopicFor(markNudged(EMPTY_TUTORIAL_STATE, "a"), topics, "/variable-income")?.id).toBe("c");
  });

  it("casa a rota com parâmetro e ignora tela sem tópico", () => {
    expect(nudgeTopicFor(EMPTY_TUTORIAL_STATE, topics, "/variable-income/PETR4")?.id).toBe("b");
    expect(nudgeTopicFor(EMPTY_TUTORIAL_STATE, topics, "/portfolio")).toBeUndefined();
  });

  it("não avisa o tópico que o jogador já abriu", () => {
    const state = markSeen(EMPTY_TUTORIAL_STATE, "b");
    expect(nudgeTopicFor(state, topics, "/variable-income/PETR4")).toBeUndefined();
  });
});

describe("pausa da partida", () => {
  it("conta só os jogadores de verdade", () => {
    // Você e 2 bots: um humano só
    expect(countHumans([{ bot: null }, { bot: { strategy: "x" } as never }, { bot: { strategy: "y" } as never }])).toBe(1);
  });

  it("pausa sozinho com o tempo correndo, e não pausa acompanhado nem já parado", () => {
    expect(shouldPause(1, 1)).toBe(true);
    expect(shouldPause(2, 1)).toBe(false);
    expect(shouldPause(1, 0)).toBe(false);
  });

  it("retoma só o que a janela pausou e só se a velocidade segue em zero", () => {
    expect(shouldResume(true, 0)).toBe(true);
    expect(shouldResume(false, 0)).toBe(false);
    // O jogador já escolheu outra velocidade com a janela aberta
    expect(shouldResume(true, 4)).toBe(false);
  });
});
