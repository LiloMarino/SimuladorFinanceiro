import type { DebugChoice, DebugCommand } from "@/types";

export interface Completion {
  /** As escolhas que combinam com o que foi digitado, na ordem do catálogo. */
  readonly options: readonly DebugChoice[];
  /** O pedaço da palavra já digitado, que a conclusão substitui. */
  readonly token: string;
}

function tokensOf(line: string) {
  const words = line.split(/\s+/).filter(Boolean);
  // Linha vazia ou terminada em espaço: a palavra em curso é uma nova, ainda vazia
  const fresh = line === "" || /\s$/.test(line);
  return { words, fresh };
}

/** As escolhas para a palavra em curso: o nome do comando na primeira, o argumento do comando nas seguintes. */
export function completionOf(line: string, commands: readonly DebugCommand[]): Completion {
  const { words, fresh } = tokensOf(line);
  const token = fresh ? "" : (words.at(-1) ?? "");
  const position = fresh ? words.length : words.length - 1;

  const choices: readonly DebugChoice[] =
    position === 0
      ? commands.map((command) => ({ value: command.name, label: command.help }))
      : (commands.find((command) => command.name === words[0])?.arguments[position - 1]?.choices ?? []);

  const wanted = token.toLowerCase();
  return { options: choices.filter((choice) => choice.value.toLowerCase().startsWith(wanted)), token };
}

function commonPrefix(values: readonly string[]) {
  return values.reduce((prefix, value) => {
    let size = 0;
    while (size < prefix.length && size < value.length && prefix[size]?.toLowerCase() === value[size]?.toLowerCase()) {
      size++;
    }
    return prefix.slice(0, size);
  });
}

/** A linha depois do Tab: uma só opção vira a palavra inteira mais um espaço; várias avançam até o prefixo comum. */
export function applyCompletion(line: string, { options, token }: Completion): string {
  const [first, ...rest] = options;
  if (!first) return line;
  const head = line.slice(0, line.length - token.length);
  if (rest.length === 0) return `${head}${first.value} `;
  return `${head}${commonPrefix(options.map((option) => option.value))}`;
}
