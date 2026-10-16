const segmenter = new Intl.Segmenter("pt-BR", { granularity: "grapheme" });

const letters = (text: string) => Array.from(segmenter.segment(text), (s) => s.segment);

/**
 * Sigla de duas letras do apelido: duas palavras dão a inicial de cada, uma palavra
 * dá as duas primeiras letras e um caractere só é dobrado. Acento e emoji contam
 * como uma letra inteira.
 */
export function playerInitials(nickname: string) {
  const [first = "", second] = nickname.trim().split(/\s+/);
  const firstLetters = letters(first);

  const initials = second
    ? [firstLetters[0], letters(second)[0]]
    : firstLetters.length > 1
      ? firstLetters.slice(0, 2)
      : [firstLetters[0], firstLetters[0]];

  return initials.join("").toLocaleUpperCase("pt-BR");
}
