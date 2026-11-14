export const FUND_NAME_MIN_LENGTH = 3;
export const FUND_NAME_MAX_LENGTH = 40;
export const TICKER_LETTERS = 4;
const TICKER_SUFFIX = "11";

/** As quatro letras da sigla ganham o sufixo 11: "AURO" → "AURO11". */
export const tickerOf = (letters: string) => `${letters}${TICKER_SUFFIX}`;

/** O campo da sigla aceita só letras, em maiúsculas, até quatro. */
export const cleanTickerLetters = (value: string) =>
  value
    .toUpperCase()
    .replace(/[^A-Z]/g, "")
    .slice(0, TICKER_LETTERS);
