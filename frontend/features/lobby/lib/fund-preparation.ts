import { z } from "zod";
import type { BotTicker, FundIdentity, Preparations } from "@/types";

const FUND_NAME_MIN_LENGTH = 3;
export const FUND_NAME_MAX_LENGTH = 40;
const TICKER_LETTERS = 4;
const TICKER_SUFFIX = "11";

/** Uma gestora que um jogador da sala vai fundar no 1º dia. */
export type PreparedFund = Preparations["funds"][number];

/** O formulário guarda as quatro letras da sigla; o sufixo 11 é fixo e entra na conversão para a API. */
export const fundFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(FUND_NAME_MIN_LENGTH, `O nome tem de ${FUND_NAME_MIN_LENGTH} a ${FUND_NAME_MAX_LENGTH} letras.`)
    .max(FUND_NAME_MAX_LENGTH, `O nome vai até ${FUND_NAME_MAX_LENGTH} letras.`),
  letters: z.string().regex(/^[A-Z]{4}$/, "A sigla tem 4 letras."),
});

export type FundForm = z.infer<typeof fundFormSchema>;

const BLANK_FUND_FORM: FundForm = { name: "", letters: "" };

/** A sigla salva ("AURO11") vira as quatro letras do campo. */
export function fundToForm(saved: FundIdentity | null): FundForm {
  return saved ? { name: saved.name, letters: saved.ticker.slice(0, TICKER_LETTERS) } : BLANK_FUND_FORM;
}

/** O formulário completo vira a identidade da API: nome sem bordas e sigla com o 11. */
export function fundFromForm(form: FundForm): FundIdentity {
  return { name: form.name.trim(), ticker: tickerOf(form.letters) };
}

export const tickerOf = (letters: string) => `${letters}${TICKER_SUFFIX}`;

/** O campo da sigla aceita só letras, em maiúsculas, até quatro. */
export const cleanTickerLetters = (value: string) =>
  value
    .toUpperCase()
    .replace(/[^A-Z]/g, "")
    .slice(0, TICKER_LETTERS);

const sameName = (a: string, b: string) => a.trim().toLowerCase() === b.trim().toLowerCase();

/** As gestoras dos outros jogadores da sala: contra elas o nome e a sigla são conferidos. */
export const rivalFunds = (preparations: Preparations, nickname: string) =>
  preparations.funds.filter((fund) => fund.nickname !== nickname);

/** Os jogadores que já preparam uma gestora com o mesmo nome (sem diferenciar maiúsculas). */
export const nameOwners = (name: string, rivals: PreparedFund[]) =>
  name.trim() === "" ? [] : rivals.filter((fund) => sameName(fund.name, name)).map((fund) => fund.nickname);

export type TickerHint =
  /** Faltam letras para conferir */
  | { status: "incomplete" }
  | { status: "free" }
  /** As quatro letras já são de ações da partida */
  | { status: "asset"; assets: string[] }
  /** Outro jogador da sala preparou a mesma sigla */
  | { status: "taken"; owners: string[] };

/**
 * O que dá para saber da sigla antes de iniciar: ações da partida com as mesmas quatro letras e
 * as gestoras dos outros jogadores. A conferência definitiva é a do servidor, nos conflitos da sala.
 */
export function tickerHint(letters: string, assets: BotTicker[], rivals: PreparedFund[]): TickerHint {
  if (letters.length < TICKER_LETTERS) return { status: "incomplete" };
  const sameLetters = assets.map((asset) => asset.ticker).filter((ticker) => ticker.replace(/\d+$/, "") === letters);
  if (sameLetters.length > 0) return { status: "asset", assets: sameLetters };
  const ticker = tickerOf(letters);
  const owners = rivals.filter((fund) => fund.ticker === ticker).map((fund) => fund.nickname);
  return owners.length > 0 ? { status: "taken", owners } : { status: "free" };
}

/** Se a gestora que o jogador preparou entra em algum conflito da sala: nome, sigla ou letras de ativo. */
export function hasFundConflict(preparations: Preparations, nickname: string) {
  const mine = preparations.funds.find((fund) => fund.nickname === nickname);
  if (!mine) return false;
  const rivals = rivalFunds(preparations, nickname);
  return (
    nameOwners(mine.name, rivals).length > 0 ||
    rivals.some((fund) => fund.ticker === mine.ticker) ||
    preparations.fund_conflicts.some((conflict) => conflict.startsWith(`${nickname}:`))
  );
}

export type FundTabBadge = { label: string; variant: "outline" | "destructive" | "fund" };

/** O selo da aba Gestora: a expansão desligada, o conflito ou a sigla preparada; sem selo quando nada foi escolhido. */
export function fundTabBadge(enabled: boolean, preparations: Preparations, nickname: string): FundTabBadge | null {
  if (!enabled) return { label: "desligada nas regras", variant: "outline" };
  const mine = preparations.funds.find((fund) => fund.nickname === nickname);
  if (!mine) return null;
  return hasFundConflict(preparations, nickname)
    ? { label: "em conflito", variant: "destructive" }
    : { label: mine.ticker, variant: "fund" };
}

/** A escolha que a aba abre mostrando: a que o servidor guarda para o jogador. */
export const fundChoice = (preparations: Preparations, nickname: string): "FOUND" | "NONE" =>
  preparations.funds.some((fund) => fund.nickname === nickname) ? "FOUND" : "NONE";
