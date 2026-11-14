import { playerColorStyle } from "@/shared/lib/player-colors";
import { playerInitials } from "@/shared/lib/player-initials";
import type { Order } from "@/types";

type Owner = Order["owner"];

/** Quem olha o livro: o apelido do jogador e, com uma gestora ativa, o nome dela. */
export type BookViewer = { nickname: string | undefined; fundName: string | null };

/** Donos que não são pessoas nem gestoras: o nome vem do servidor, a sigla é fixa. */
const SYNTHETIC_LABEL: Partial<Record<Owner, string>> = {
  market: "B3",
  fund_maker: "FM",
  fund_issuer: "OP",
};

export type OwnerBadge = {
  /** Sigla do selo */
  label: string;
  /** `player` usa a cor do jogador; `fund` a da gestora; `neutral` o cinza de bots e donos sintéticos */
  tone: "player" | "fund" | "neutral";
  /** Fundo e texto da cor do jogador (só no tom `player`) */
  color: { background: string; foreground: string } | null;
};

/** O selo de quem pôs a ordem: o jogador na cor dele, a gestora na dela, o resto em cinza. */
export function ownerBadge(order: Order): OwnerBadge {
  const synthetic = SYNTHETIC_LABEL[order.owner];
  if (synthetic) return { label: synthetic, tone: "neutral", color: null };
  const label = playerInitials(order.player_nickname);
  if (order.owner === "bot") return { label, tone: "neutral", color: null };
  if (order.owner === "fund") return { label, tone: "fund", color: null };
  return { label, tone: "player", color: playerColorStyle(order.player_color ?? undefined) };
}

/** A ordem veio de um dono sintético (Mercado, formador ou oferta pública), sem pessoa por trás. */
export const isSyntheticOwner = (order: Order) => order.owner in SYNTHETIC_LABEL;

/** A ordem é da conta ativa: do jogador na conta pessoal, ou da gestora quando ela está ativa. */
export function ownsOrder(order: Order, viewer: BookViewer) {
  if (viewer.fundName !== null) return order.owner === "fund" && order.player_nickname === viewer.fundName;
  return order.owner === "player" && order.player_nickname === viewer.nickname;
}
